from src.services.batch_processor import BatchProcessor
from src.services.suggestion_chain import ChainConfig


def test_batch_processor(mocker):
    mock_llm_judge = mocker.MagicMock()
    mock_llm_judge.get_feedback.return_value = {"feedback": "Replace 'significant' with a specific term."}

    texts = ["Text 1", "Text 2"]
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_judge)

    results = batch_processor.process_batch(texts, ChainConfig(
        mode="improvement_prompt",
        vale_rules=[],
        llm_templates=["improvement_prompt"]
    ))
    assert results is not None
