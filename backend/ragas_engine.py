"""
RAGAS + DeepEval Integrated Evaluation Engine
- Async caching
- Summarized reasoning
- Combined metrics (DeepEval + RAGAS)
- Uses all recommended + optional RAGAS metrics
"""

import asyncio
from deepeval_utils import evaluate_rag
from ragas import evaluate as ragas_evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
    answer_similarity,
    multimodal_faithness,
    multimodal_relevance
)
from datasets import Dataset
from cache import answers_cache
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Evaluate RAGAS metrics
# -------------------------
def evaluate_ragas(question: str, answer: str, context: list):
    """
    Run RAGAS metrics for a single question-answer-context trio.
    Supports all recommended + optional metrics.
    """
    scores_dict = {}
    try:
        # Normalize context
        if isinstance(context, str):
            context = [context]
        elif isinstance(context, list):
            context = [str(c).strip() for c in context if c]

        data = {
            "question": [question],
            "answer": [answer],
            "contexts": [context],
            "reference": [answer],  # Required for context-based metrics
        }

        dataset = Dataset.from_dict(data)

        # Metrics to evaluate
        metrics_list = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness,
            answer_similarity,
            multimodal_faithness,
            multimodal_relevance
        ]

        ragas_results = ragas_evaluate(dataset=dataset, metrics=metrics_list)

        # Directly extract values from EvaluationResult, just like your previous working code
        scores_dict = {
            "Faithfulness": float(ragas_results["faithfulness"][0]),
            "AnswerRelevancy": float(ragas_results["answer_relevancy"][0]),
            "ContextPrecision": float(ragas_results["context_precision"][0]),
            "ContextRecall": float(ragas_results["context_recall"][0]),
            "AnswerCorrectness": float(ragas_results["answer_correctness"][0]),
            "AnswerSimilarity": float(ragas_results["answer_similarity"][0]),
            "MultiModalFaithfulness": float(ragas_results["faithful_rate"][0]),
            "MultiModalRelevance": float(ragas_results["relevance_rate"][0]),
        }

    except Exception as e:
        print(f"[RAGAS] Evaluation failed: {e}")

    return scores_dict

# -------------------------
# Generate answer + reasoning + metrics
# -------------------------
async def ragas_generate(question: str, summarize: bool = True):
    """Generate RAG answer + reasoning and compute metrics asynchronously."""
    from rag_engine import query_rag  # dynamic import to avoid circular dependency
    answer, context, relevant = await asyncio.to_thread(query_rag, question)
    reasoning = None

    if relevant and context:
        clean_context = [c.replace("\t", " ").replace("\n", " ").strip() for c in context]

        # Summarize reasoning
        if summarize:
            prompt = (
                "Summarize the following retrieved context into a concise, readable explanation "
                "that clearly answers the user's question:\n\n" + "\n".join(clean_context)
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
                print(f"[Summarization] Failed: {e}")
                reasoning = "\n".join(clean_context)
        else:
            reasoning = "\n".join(clean_context)

        # Compute metrics asynchronously (background task)
        asyncio.create_task(compute_metrics_async(question, answer, context, reasoning))

    return answer, context, reasoning, relevant

# -------------------------
# Compute metrics async
# -------------------------
async def compute_metrics_async(question, answer, context, reasoning):
    """Compute both DeepEval and RAGAS metrics asynchronously and cache results."""
    try:
        print(f"[Metrics] Starting computation for: {question}")

        deepeval_scores = await asyncio.to_thread(evaluate_rag, question, answer, context)
        print(f"[Metrics] DeepEval done for: {question}")

        ragas_scores = await asyncio.to_thread(evaluate_ragas, question, answer, context)
        print(f"[Metrics] RAGAS done for: {question}")

        combined_scores = {"DeepEval": deepeval_scores, "RAGAS": ragas_scores}

        # Update cache
        if question in answers_cache:
            answers_cache[question]["metrics"] = combined_scores
            answers_cache[question]["reasoning"] = reasoning

        print(f"[Metrics] Completed for: {question}")

    except Exception as e:
        print(f"[Metrics] Computation failed: {e}")