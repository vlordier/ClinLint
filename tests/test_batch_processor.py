import pytest
from app.services.batch_processor import BatchProcessor
from app.services.suggestion_chain import AnalysisMode, ChainConfig
from app.services.llm_feedback import LLMFeedback

@pytest.fixture
def mock_llm_feedback(mocker):
    """Create a mock LLMFeedback instance."""
    mock = mocker.Mock(spec=LLMFeedback)
    mock.get_feedback.return_value = {"feedback": ["Test feedback"]}
    return mock

@pytest.mark.parametrize("texts, expected_count", [
    (["Text 1", "Text 2"], 2),
    (["Single text"], 1),
    ([], 0)
])
def test_batch_processor_basic(mock_llm_feedback, texts, expected_count):
    """Test basic batch processing with different input sizes."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)
    results = batch_processor.process_batch(texts, ChainConfig(
        mode=AnalysisMode.LLM_ONLY,
        vale_rules=[],
        llm_templates=["improvement_prompt"]
    ))

    assert results is not None
    assert len(results) == expected_count

    if results:
        for result in results:
            assert "llm" in result
            assert isinstance(result["llm"]["feedback"], (str, dict, list))
            if isinstance(result["llm"]["feedback"], list):
                assert all(isinstance(item, (str, dict)) for item in result["llm"]["feedback"])

@pytest.mark.parametrize("mode", [
    AnalysisMode.VALE_ONLY,
    AnalysisMode.LLM_ONLY,
    AnalysisMode.COMBINED
])
def test_batch_processor_modes(mock_llm_feedback, sample_texts, mode):
    """Test batch processing with different analysis modes."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)
    results = batch_processor.process_batch(sample_texts[:2], ChainConfig(
        mode=mode,
        vale_rules=["CSR.Precision", "CSR.Terminology"],
        llm_templates=["improvement_prompt"]
    ))

    assert len(results) == 2
    for result in results:
        if mode in [AnalysisMode.VALE_ONLY, AnalysisMode.COMBINED]:
            assert "vale" in result
        if mode in [AnalysisMode.LLM_ONLY, AnalysisMode.COMBINED]:
            assert "llm" in result

def test_batch_processor_error_handling(mock_llm_feedback):
    """Test batch processor error handling."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)

    # Test with invalid input
    with pytest.raises(ValueError):
        batch_processor.process_batch(None, ChainConfig(
            mode=AnalysisMode.LLM_ONLY,
            llm_templates=["improvement_prompt"]
        ))

    # Test with invalid config
    with pytest.raises(TypeError):
        batch_processor.process_batch(["text"], None)

def test_batch_processor_concurrent_execution(mock_llm_feedback, sample_texts):
    """Test concurrent execution of batch processing."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)

    # Process a larger batch to test concurrency
    results = batch_processor.process_batch(sample_texts, ChainConfig(
        mode=AnalysisMode.COMBINED,
        vale_rules=["CSR.Precision"],
        llm_templates=["improvement_prompt"]
    ))

    assert len(results) == len(sample_texts)
    assert all("vale" in r and "llm" in r for r in results)

def test_batch_processor_empty_rules(mock_llm_feedback, sample_texts):
    """Test batch processing with empty rule sets."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)

    results = batch_processor.process_batch(sample_texts[:2], ChainConfig(
        mode=AnalysisMode.COMBINED,
        vale_rules=[],
        llm_templates=[]
    ))

    assert len(results) == 2
    for result in results:
        assert "vale" in result
        assert "llm" in result

def test_process_single_error_handling(mock_llm_feedback):
    """Test error handling in process_single."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)
    
    # Test with invalid text that should raise an error
    with pytest.raises(ValueError):
        batch_processor.process_batch([None], ChainConfig(
            mode=AnalysisMode.LLM_ONLY,
            llm_templates=["improvement_prompt"]
        ))

def test_thread_local_storage(mock_llm_feedback, sample_texts):
    """Test thread-local storage behavior."""
    batch_processor = BatchProcessor("config/rules/final-template.ini", mock_llm_feedback)
    
    # Process multiple texts to trigger thread-local storage
    results = batch_processor.process_batch(sample_texts[:3], ChainConfig(
        mode=AnalysisMode.COMBINED,
        vale_rules=["CSR.Precision"],
        llm_templates=["improvement_prompt"]
    ), max_workers=2)  # Force multiple threads
    
    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results)
