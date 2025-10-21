"""
- synchronous and async hallucinated
"""

from typing import Dict, Any
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase
from deepeval import evaluate

def evaluate_rag(question: str, answer: str, context: list) -> Dict[str, Any]:
    """
    Evaluate a RAG answer using DeepEval.
    Returns scores, reasons, and pass/fail for faithfulness and relevance.
    """
    scores_dict = {
        "FaithfulnessMetric": {"value": 0.0, "reason": "No context provided or answer too generic", "pass": False},
        "AnswerRelevancyMetric": {"value": 0.0, "reason": "No context provided or answer too generic", "pass": False}
    }

    try:
        if context and answer.strip():
            llm_model = GPTModel()

            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                context=context,
                retrieval_context=context
            )

            metrics = [FaithfulnessMetric(model=llm_model), AnswerRelevancyMetric(model=llm_model)]
            evaluation_results = evaluate([test_case], metrics)

            # DeepEval latest API returns test_results → metrics_data → name, score, reason, success
            test_results_list = getattr(evaluation_results, "test_results", evaluation_results)
            for test_result in test_results_list:
                for metric_data in getattr(test_result, "metrics_data", []):
                    name = metric_data.name.replace(" ", "") + "Metric"
                    reason = metric_data.reason
                    score = metric_data.score
                    success = metric_data.success

                    # Customize reason if score is 0
                    if score == 0.0:
                        if "Faithfulness" in name:
                            reason = "Answer does not explicitly use the retrieved context."
                        else:
                            reason = "Answer does not sufficiently match the context in relevance."

                    scores_dict[name] = {
                        "value": score,
                        "reason": reason,
                        "pass": success
                    }

    except Exception as e:
        print(f"DeepEval evaluation failed: {e}")

    # Print metrics summary to terminal
    print("\n--- DeepEval RAG Results ---")
    for metric_name, metric_data in scores_dict.items():
        print(f"{metric_name}: {metric_data['value']} | Reason: {metric_data['reason']} | Pass: {metric_data['pass']}")
    print("-------------------------------\n")

    return scores_dict