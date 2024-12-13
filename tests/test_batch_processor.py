from services.batch_processor import BatchProcessor
from services.llm_judge import LLMJudge

def test_batch_processor(mocker):
    mock_llm_judge = mocker.MagicMock()
    mock_llm_judge.get_feedback.return_value = {"feedback": "Replace 'significant' with a specific term."}

    texts = ["Text 1", "Text 2"]
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_judge)

    results = batch_processor.process_batch(texts, "improvement_prompt")
    assert len(results) == len(texts)
    for result in results:
        assert "suggestions" in result
