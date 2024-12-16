import pytest
from app.schemas.vocabulary_schemas import VocabularyUpdate
from app.services.vocabulary_validator import VocabularyValidator

@pytest.fixture
def valid_vocabularies():
    """Create a list of valid vocabulary updates."""
    return [
        VocabularyUpdate(
            terms=["term1", "term2"],
            category="medical",
            type="accept"
        ),
        VocabularyUpdate(
            terms=["term3", "term4"],
            category="statistical",
            type="reject"
        )
    ]

@pytest.fixture
def invalid_vocabularies():
    """Create a list of invalid vocabulary updates."""
    return [
        VocabularyUpdate(
            terms=[],  # Empty terms list
            category="medical",
            type="accept"
        ),
        VocabularyUpdate(
            terms=["term1"],
            category="invalid_category",  # Invalid category
            type="accept"
        )
    ]

def test_batch_validation_valid_vocabularies(valid_vocabularies):
    """Test batch validation with valid vocabularies."""
    validator = VocabularyValidator()
    results = validator.validate_vocabularies_batch(valid_vocabularies)

    assert len(results) == len(valid_vocabularies)
    assert all(result["is_valid"] for result in results)
    assert all(not result["errors"] for result in results)

def test_batch_validation_invalid_vocabularies(invalid_vocabularies):
    """Test batch validation with invalid vocabularies."""
    validator = VocabularyValidator()
    results = validator.validate_vocabularies_batch(invalid_vocabularies)

    assert len(results) == len(invalid_vocabularies)
    assert not any(result["is_valid"] for result in results)
    assert all(result["errors"] for result in results)

def test_batch_validation_mixed_vocabularies(valid_vocabularies, invalid_vocabularies):
    """Test batch validation with mix of valid and invalid vocabularies."""
    validator = VocabularyValidator()
    mixed_vocabularies = valid_vocabularies + invalid_vocabularies
    results = validator.validate_vocabularies_batch(mixed_vocabularies)

    assert len(results) == len(mixed_vocabularies)
    assert any(result["is_valid"] for result in results)
    assert any(not result["is_valid"] for result in results)

def test_batch_validation_empty_list():
    """Test batch validation with empty vocabularies list."""
    validator = VocabularyValidator()
    results = validator.validate_vocabularies_batch([])

    assert isinstance(results, list)
    assert len(results) == 0

def test_batch_validation_concurrent(valid_vocabularies):
    """Test concurrent batch validation of vocabularies."""
    import concurrent.futures

    validator = VocabularyValidator()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(validator.validate_vocabulary, vocab)
            for vocab in valid_vocabularies
        ]
        results = [future.result() for future in futures]

    assert len(results) == len(valid_vocabularies)
    assert all(result["is_valid"] for result in results)
