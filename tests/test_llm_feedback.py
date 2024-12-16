import pytest
from app.services.llm_feedback import LLMFeedback
from app.services.config_loader import ConfigLoader

@pytest.fixture
def mock_config_loader(mocker):
    mock_loader = mocker.Mock(spec=ConfigLoader)
    mock_loader.get_prompt_dir.return_value = "app/prompts"
    return mock_loader

def test_load_prompt(mock_config_loader):
    llm_feedback = LLMFeedback("v1", mock_config_loader)
    prompt = llm_feedback.load_prompt("generic_prompt")
    assert prompt is not None
    assert "template" in prompt.template
