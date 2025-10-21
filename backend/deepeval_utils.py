"""
- DeepEval: few more pre-built and custom metrics
"""

from typing import Dict, Any
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    HallucinationMetric,
    # SummarizationMetric,
    ContextualRelevancyMetric
)
from deepeval_fluency import FluencyMetric  # import the custom metric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase
from deepeval import evaluate

def evaluate_rag(question: str, answer: str, context: list) -> Dict[str, Any]:
    scores_dict = {}
    try:
        if context and answer.strip():
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
                # SummarizationMetric(model=llm_model),
                ContextualRelevancyMetric(model=llm_model),
                FluencyMetric() # ✅ do not pass model here
            ]
            evaluation_results = evaluate([test_case], metrics)

            test_results_list = getattr(evaluation_results, "test_results", evaluation_results)
            for test_result in test_results_list:
                for metric_data in getattr(test_result, "metrics_data", []):
                    name = metric_data.name.replace(" ", "") + "Metric"
                    scores_dict[name] = {
                        "value": metric_data.score,
                        "reason": metric_data.reason,
                        "pass": metric_data.success
                    }

    except Exception as e:
        print(f"DeepEval evaluation failed: {e}")

    return scores_dict