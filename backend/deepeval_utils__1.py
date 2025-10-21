"""
- DeepEval: few more pre-built and custom metrics
- RAGAS: retrieval and generation quality metrics
"""

from typing import Dict, Any
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    HallucinationMetric,
    ContextualRelevancyMetric
)
from deepeval_fluency import FluencyMetric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase
from deepeval import evaluate

# --- RAGAS imports ---
from datasets import Dataset
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas import evaluate as evaluate_ragas


def evaluate_rag(question: str, answer: str, context: list) -> Dict[str, Any]:
    deepeval_scores = {}
    ragas_scores = {}

    try:
        if context and answer.strip():
            # --- DeepEval metrics ---
            llm_model = GPTModel()
            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                context=context,
                retrieval_context=context
            )

            metrics = [
                FaithfulnessMetric(model=llm_model),
                AnswerRelevancyMetric(model=llm_model),
                HallucinationMetric(model=llm_model),
                ContextualRelevancyMetric(model=llm_model),
                FluencyMetric()
            ]

            evaluation_results = evaluate([test_case], metrics)
            test_results_list = getattr(evaluation_results, "test_results", evaluation_results)

            for test_result in test_results_list:
                for metric_data in getattr(test_result, "metrics_data", []):
                    name = metric_data.name.replace(" ", "") + "Metric"
                    deepeval_scores[name] = {
                        "value": metric_data.score,
                        "reason": metric_data.reason,
                        "pass": metric_data.success
                    }

            # --- RAGAS metrics ---
            # Join context chunks into a single string per example
            # joined_context = " ".join(context).replace("\t", " ").replace("\n", " ").strip()

            ragas_data = {
                "question": [question],
                "answer": [answer],
                # "contexts": [joined_context],  # now proper list of strings
                "contexts": [context],   # context is already a list of strings
                "reference": [answer],         # required by ContextPrecision/Recall
            }

            ragas_dataset = Dataset.from_dict(ragas_data)

            faithfulness = Faithfulness()
            answer_relevance = AnswerRelevancy()
            context_precision = ContextPrecision()
            context_recall = ContextRecall()

            ragas_results = evaluate_ragas(
                dataset=ragas_dataset,
                metrics=[faithfulness, answer_relevance, context_precision, context_recall],
            )

            # Convert single-item lists to floats
            # ragas_scores = {
            #     "Faithfulness": float(ragas_results["faithfulness"][0]),
            #     "AnswerRelevance": float(ragas_results["answer_relevance"][0]),
            #     "ContextPrecision": float(ragas_results["context_precision"][0]),
            #     "ContextRecall": float(ragas_results["context_recall"][0]),
            # }
            ragas_scores = {}
            for key, value in ragas_results.items():
                # Convert single-item lists to float
                ragas_scores[key] = float(value[0]) if isinstance(value, list) and value else 0.0


    except Exception as e:
        print(f"Evaluation failed: {e}")

    # Return separated sections for UI clarity
    return {
        "deepeval_scores": deepeval_scores,
        "ragas_scores": ragas_scores
    }