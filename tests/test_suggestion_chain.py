import pytest
from services.suggestion_chain import SuggestionChain
from services.llm_judge import LLMJudge

@pytest.fixture
def mock_llm_judge():
    class MockLLMJudge:
        def get_feedback(self, text, prompt_template, **kwargs):
            return {"feedback": "Replace 'significant' with a specific term."}

    return MockLLMJudge()

def test_generate_suggestions(mock_llm_judge):
    text = "The patient showed significant improvement."
    vale_config = "config/rules/final-template.ini"
    suggestion_chain = SuggestionChain(vale_config, mock_llm_judge)

    result = suggestion_chain.generate_suggestions(
        text, llm_template="improvement_prompt"
    )

    assert "vale_issues" in result
    assert "suggestions" in result
