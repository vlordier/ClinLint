import pytest
from pydantic import ValidationError

from app.services.rule_validator import RuleValidator
from app.schemas.vale_package_schema import RuleDefinition, RuleType, RuleSeverity, RuleScope

@pytest.fixture
def valid_rules():
    """Create a list of valid rule definitions."""
    return [
        RuleDefinition(
            extends=RuleType.EXISTENCE,
            message="Test rule 1",
            level=RuleSeverity.WARNING,
            scope=RuleScope.TEXT
        ),
        RuleDefinition(
            extends=RuleType.SUBSTITUTION,
            message="Test rule 2",
            level=RuleSeverity.ERROR,
            scope=RuleScope.PARAGRAPH
        )
    ]

@pytest.fixture
def invalid_rules():
    """Create a list of invalid rule definitions."""
    return [
        RuleDefinition(
            extends=RuleType.EXISTENCE,
            message="",  # Invalid empty message
            level=RuleSeverity.WARNING,
            scope=RuleScope.TEXT
        ),
        RuleDefinition(
            extends=RuleType.SUBSTITUTION,
            message="Test rule",
            level="invalid_level",  # Invalid severity level
            scope=RuleScope.PARAGRAPH
        )
    ]

def test_batch_validation_valid_rules(valid_rules):
    """Test batch validation with valid rules."""
    validator = RuleValidator()
    results = validator.validate_rules_batch(valid_rules)

    assert len(results) == len(valid_rules)
    assert all(result["is_valid"] for result in results)
    assert all(not result["errors"] for result in results)

def test_batch_validation_invalid_rules(invalid_rules):
    """Test batch validation with invalid rules."""
    validator = RuleValidator()
    results = validator.validate_rules_batch(invalid_rules)

    assert len(results) == len(invalid_rules)
    assert not any(result["is_valid"] for result in results)
    assert all(result["errors"] for result in results)

def test_batch_validation_mixed_rules(valid_rules, invalid_rules):
    """Test batch validation with mix of valid and invalid rules."""
    validator = RuleValidator()
    mixed_rules = valid_rules + invalid_rules
    results = validator.validate_rules_batch(mixed_rules)

    assert len(results) == len(mixed_rules)
    assert any(result["is_valid"] for result in results)
    assert any(not result["is_valid"] for result in results)

def test_batch_validation_with_llm(valid_rules, mocker):
    """Test batch validation with LLM assistance."""
    mock_llm = mocker.MagicMock()
    mock_llm.get_feedback.return_value = {"suggested_rule": {}}

    validator = RuleValidator(llm_judge=mock_llm)
    results = validator.validate_rules_batch(valid_rules, use_llm=True)

    assert len(results) == len(valid_rules)
    assert mock_llm.get_feedback.call_count == 0  # LLM not called for valid rules

def test_batch_validation_empty_list():
    """Test batch validation with empty rules list."""
    validator = RuleValidator()
    results = validator.validate_rules_batch([])

    assert isinstance(results, list)
    assert len(results) == 0

def test_batch_validation_concurrent(valid_rules):
    """Test concurrent batch validation of rules."""
    import concurrent.futures

    validator = RuleValidator()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(validator.validate_rule, rule)
            for rule in valid_rules
        ]
        results = [future.result() for future in futures]

    assert len(results) == len(valid_rules)
    assert all(result["is_valid"] for result in results)
