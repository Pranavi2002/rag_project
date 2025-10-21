"""
- metrics are now being stored in cache and shown fast for same query if asked again
- only deepeval metrics
"""

import asyncio
from rag_engine import query_rag
from deepeval_utils import evaluate_rag
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ragas_generate(question: str, summarize: bool = True):
    """
    RAGAS: Generate answer (from all docs) + summarized reasoning + async DeepEval metrics
    """
    # Step 1: Retrieve answer and context using existing RAG
    answer, context, relevant = await asyncio.to_thread(query_rag, question)

    reasoning = None
    if relevant and context:
        # Clean each context chunk
        clean_context = [c.replace("\t", " ").replace("\n", " ").strip() for c in context]

        if summarize:
            # Summarize reasoning using LLM
            prompt = (
                "Summarize the following retrieved context into a concise, readable explanation "
                "that answers the question clearly:\n\n"
                + "\n".join(clean_context)
            )
            try:
                response = await asyncio.to_thread(
                    lambda: client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=300,
                    )
                )
                reasoning = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"RAGAS summarization failed: {e}")
                # fallback to joined context if summarization fails
                reasoning = " ".join(clean_context)
        else:
            reasoning = "\n".join(clean_context)

        # Schedule async metric computation
        asyncio.create_task(compute_metrics_async(question, answer, context, reasoning))

    return answer, context, reasoning, relevant


async def compute_metrics_async(question, answer, context, reasoning):
    from main import answers_cache

    try:
        scores = await asyncio.to_thread(evaluate_rag, question, answer, context)
        # Save metrics + reasoning in cache
        if question in answers_cache:
            answers_cache[question]["metrics"] = scores
            answers_cache[question]["reasoning"] = reasoning
    except Exception as e:
        print(f"RAGAS metrics computation failed: {e}")