from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

class FluencyMetric(GEval):
    def __init__(self, **kwargs):
        name = "Fluency"
        evaluation_params = [LLMTestCaseParams.ACTUAL_OUTPUT]
        criteria = (
            "Evaluate whether the text is fluent and natural in English. "
            "Check for grammar, sentence structure, smoothness, and readability."
        )
        evaluation_steps = [
            "Check grammar and punctuation.",
            "Check sentence flow and readability.",
            "Check for awkward phrasing or unnatural wording."
        ]
        # Remove criteria/evaluation_steps from kwargs to avoid duplication
        kwargs.pop("name", None)
        kwargs.pop("evaluation_params", None)
        kwargs.pop('criteria', None)
        kwargs.pop('evaluation_steps', None)
        kwargs.pop("async_mode", None)
        super().__init__(
            name,
            evaluation_params,
            criteria=criteria,
            evaluation_steps=evaluation_steps,
            async_mode=False,
            **kwargs
        )