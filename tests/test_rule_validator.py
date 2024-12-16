from app.services.rule_validator import RuleValidator
from app.schemas.vale_package_schema import RuleDefinition

def test_get_llm_fixes(mocker):
    mock_llm_feedback = mocker.Mock()
    mock_llm_feedback.get_feedback.return_value = {
        "suggested_rule": {
            "extends": "existence",
            "message": "Fixed message",
            "level": "warning",
            "scope": "text"
        }
    }
    validator = RuleValidator(llm_feedback=mock_llm_feedback)
    rule = RuleDefinition(
        extends="invalid_type",
        message="Test message",
        level="warning",
        scope="text"
    )
    result = validator._get_llm_fixes(rule, ["Invalid rule type"], max_attempts=1)
    assert result["fixed_rule"] is not None
    assert result["is_valid"]
