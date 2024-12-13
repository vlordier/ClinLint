from pathlib import Path

import pytest
import yaml

from services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain


@pytest.fixture
def test_cases():
    test_data_path = Path(__file__).parent / "data" / "csr_examples.yaml"
    with open(test_data_path) as f:
        return yaml.safe_load(f)["cases"]

@pytest.fixture
def mock_llm_judge():
    class MockLLMJudge:
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

    result = suggestion_chain.generate_suggestions(
        case["text"],
        ChainConfig(
            mode=AnalysisMode.LLM_ONLY,
            vale_rules=[],
            llm_templates=["improvement_prompt"]
        )
    )
    assert result is not None
