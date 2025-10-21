"""
- shows ragas, asynchronous with deepeval
- complete reasoning
"""

import asyncio
from rag_engine import query_rag
from deepeval_utils import evaluate_rag

async def ragas_generate(question: str, summarize: bool = True):
    """
    RAGAS: Generate answer + reasoning + async DeepEval metrics
    """
    # Step 1: Retrieve answer and context using existing RAG
    answer, context, relevant = await asyncio.to_thread(query_rag, question)

    reasoning = None
    if relevant:
        # Clean each context chunk
        clean_context = [c.replace("\t", " ").strip() for c in context]
        
        if summarize:
            # Optional: use simple join as input to LLM for summarization
            # Here you can call your LLM summarize function if you want
            reasoning = " ".join(clean_context)  # simple clean join
            # Or: reasoning = await llm_summarize(clean_context)
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