"""
RAGAS + DeepEval Integrated Evaluation Engine
- Async caching
- Summarized reasoning
- Combined metrics (DeepEval + RAGAS)
"""

import asyncio
from deepeval_utils import evaluate_rag
from ragas import evaluate as ragas_evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset
# from main import answers_cache 
from cache import answers_cache
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_ragas(question: str, answer: str, context: list):
    scores_dict = {}
    try:
        data = {
            "question": [question],
            "answer": [answer],
            "contexts": [context],
            "reference": [answer]  # required for context_precision / context_recall
        }
        dataset = Dataset.from_dict(data)
        ragas_results = ragas_evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
        )
        scores_dict = {
            "Faithfulness": float(ragas_results["faithfulness"][0]),
            "AnswerRelevancy": float(ragas_results["answer_relevancy"][0]),
            "ContextPrecision": float(ragas_results["context_precision"][0]),
            "ContextRecall": float(ragas_results["context_recall"][0]),
        }
    except Exception as e:
        print(f"RAGAS evaluation failed: {e}")
    return scores_dict

async def ragas_generate(question: str, summarize: bool = True):
    from rag_engine import query_rag  # or wherever your RAG function is
    answer, context, relevant = await asyncio.to_thread(query_rag, question)
    reasoning = None

    if relevant and context:
        clean_context = [c.replace("\t", " ").replace("\n", " ").strip() for c in context]

        if summarize:
            prompt = (
                "Summarize the following retrieved context into a concise, readable explanation "
                "that answers the question clearly:\n\n" + "\n".join(clean_context)
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
                reasoning = "\n".join(clean_context)
        else:
            reasoning = "\n".join(clean_context)

        # Run metrics asynchronously but do not block query
        asyncio.create_task(compute_metrics_async(question, answer, context, reasoning))

    return answer, context, reasoning, relevant

async def compute_metrics_async(question, answer, context, reasoning):
    from cache import answers_cache
    try:
        deepeval_scores = await asyncio.to_thread(evaluate_rag, question, answer, context)
        ragas_scores = await asyncio.to_thread(evaluate_ragas, question, answer, context)

        combined_scores = {
            "DeepEval": deepeval_scores,
            "RAGAS": ragas_scores
        }

        if question in answers_cache:
            answers_cache[question]["metrics"] = combined_scores
            answers_cache[question]["reasoning"] = reasoning

        print(f"Metrics computed for question: {question}")
    except Exception as e:
        print(f"Metrics computation failed: {e}")