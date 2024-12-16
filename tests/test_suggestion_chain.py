from pathlib import Path

import pytest
import yaml

from app.services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain


@pytest.fixture
def test_cases() -> dict:
    test_data_path = Path(__file__).parent / "data" / "csr_examples.yaml"
    with open(test_data_path) as f:
        return yaml.safe_load(f)["cases"]

@pytest.fixture
def mock_llm_feedback():
    """Create a mock LLMFeedback instance."""
    from services.llm_feedback import LLMFeedback

    class MockLLMFeedback(LLMFeedback):
        def __init__(self):
            pass

        def get_feedback(self, prompt_template, **kwargs):
            text = kwargs.get('text', '')
            if "significant" in text.lower():
                return {
                    "feedback": [
                        "Replace 'significant' with quantifiable metrics",
                        "Use 'subject' instead of 'patient'"
                    ]
                }
            elif "approximately" in text.lower():
                return {
                    "feedback": ["State the exact percentage of subjects"]
                }
            return {"feedback": ["Improve clarity and precision"]}

    return MockLLMFeedback()

@pytest.fixture
def mock_vale_runner(mocker):
    def _mock_vale_runner(output):
        mock = mocker.patch("services.vale_runner.run_vale_on_text")
        mock.return_value = output
        return mock
    return _mock_vale_runner
    from services.llm_judge import LLMJudge

    class MockLLMJudge(LLMJudge):
        def __init__(self):
            pass

        def get_feedback(self, prompt_template, **kwargs):
            text = kwargs.get('text', '')
            if "significant" in text.lower():
                return {
                    "feedback": [
                        "Replace 'significant' with quantifiable metrics",
                        "Use 'subject' instead of 'patient'"
                    ]
                }
            elif "approximately" in text.lower():
                return {
                    "feedback": ["State the exact percentage of subjects"]
                }
            return {"feedback": ["Improve clarity and precision"]}

    return MockLLMJudge()

@pytest.mark.parametrize("case_id", ["vague-terms", "measurement-precision", "terminology-consistency"])
def test_generate_suggestions(mock_llm_judge, test_cases, case_id):
    case = next(c for c in test_cases if c["id"] == case_id)
    vale_config = ".vale/styles/CSR/rules.yml"
    suggestion_chain = SuggestionChain(vale_config, mock_llm_judge)

    config = ChainConfig(
        mode=AnalysisMode.LLM_ONLY,
        vale_rules=[],
        llm_templates=["improvement_prompt"]
    )
    result = suggestion_chain.generate_suggestions(
        case["text"],
        config=config
    )
    assert result is not None

def test_invalid_vale_config(mock_llm_judge):
    with pytest.raises(ValueError, match="Invalid Vale configuration path."):
        SuggestionChain(None, mock_llm_judge)

def test_run_vale_analysis(mock_llm_judge):
    suggestion_chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
    text = "The patient showed significant improvement."
    rules = ["CSR.Precision"]
    result = suggestion_chain._run_vale_analysis(text, rules)
    assert "vale_issues" in result
    assert isinstance(result["vale_issues"], dict)

def test_run_llm_analysis(mock_llm_judge):
    suggestion_chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
    text = "The patient showed significant improvement."
    templates = ["improvement_prompt"]
    result = suggestion_chain._run_llm_analysis(text, templates)
    assert "feedback" in result
    assert isinstance(result["feedback"], list)
