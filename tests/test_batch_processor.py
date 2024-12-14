from services.batch_processor import BatchProcessor
from services.suggestion_chain import ChainConfig


def test_batch_processor(mocker):
    from services.llm_judge import LLMJudge

    mock_config_loader = mocker.MagicMock()
    mock_config_loader.get_llm_config.return_value = {
        "openai": {
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 500
        }
    }

    class MockLLMJudge(LLMJudge):
        def __init__(self, version="v1", config_loader=None):
            self.version = version
            self.config_loader = config_loader

        def get_feedback(self, prompt_template, **kwargs):
            return {"feedback": "Replace 'significant' with a specific term."}

    mock_llm_judge = MockLLMJudge(version="v1", config_loader=mock_config_loader)
    texts = ["Text 1", "Text 2"]
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_judge)

    results = batch_processor.process_batch(texts, ChainConfig(
        mode="llm_only",
        vale_rules=[],
        llm_templates=["improvement_prompt"]
    ))
    assert results is not None
