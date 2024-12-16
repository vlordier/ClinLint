import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_validate_rule_basic():
    """Test basic rule validation without LLM."""
    rule = {
        "extends": "existence",
        "message": "Use 'clinical trial' instead of 'study'",
        "level": "warning",
        "scope": "text"
    }
    response = client.post("/validate/rule", json=rule)
    response.raise_for_status()
    if not response.json()["is_valid"]:
        pytest.fail("Expected rule to be valid, but it was not.")

def test_validate_rule_invalid():
    """Test validation of invalid rule."""
    rule = {
        "extends": "invalid_type",  # Invalid rule type
        "message": "Test message",
        "level": "warning",
        "scope": "text"
    }
    response = client.post("/validate/rule", json=rule)
    response.raise_for_status()
    if response.json()["is_valid"]:
        pytest.fail("Expected rule to be invalid, but it was valid.")
    if len(response.json()["errors"]) == 0:
        pytest.fail("Expected errors in response, but none were found.")

def test_validate_rule_with_llm(mocker):
    """Test rule validation with LLM assistance."""
    # Mock LLM judge
    mock_feedback = {
        "suggested_rule": {
            "extends": "existence",
            "message": "Fixed message",
            "level": "warning",
            "scope": "text"
        }
    }
    mocker.patch("services.llm_judge.LLMJudge.get_feedback", return_value=mock_feedback)

    rule = {
        "extends": "invalid_type",
        "message": "Test message",
        "level": "warning",
        "scope": "text"
    }
    response = client.post("/validate/rule", params={"use_llm": True}, json=rule)
    response.raise_for_status()
    data = response.json()
    if "llm_conversation" not in data:
        pytest.fail("Expected 'llm_conversation' in response, but it was not found.")
    if data["fixed_rule"] is None:
        pytest.fail("Expected a fixed rule in response, but none was found.")

def test_validate_rule_llm_multiple_attempts(mocker):
    """Test multiple LLM fix attempts."""
    # Mock LLM judge to fail twice then succeed
    attempts = []
    def mock_feedback(self, template, **kwargs):
        attempts.append(1)
        if len(attempts) < 3:
            return {"suggested_rule": {"extends": "invalid_type"}}
        return {
            "suggested_rule": {
                "extends": "existence",
                "message": "Fixed message",
                "level": "warning",
                "scope": "text"
            }
        }

    mocker.patch("services.llm_judge.LLMJudge.get_feedback", mock_feedback)

    rule = {
        "extends": "invalid_type",
        "message": "Test message",
        "level": "warning",
        "scope": "text"
    }
    response = client.post("/validate/rule", params={"use_llm": True}, json=rule)
    response.raise_for_status()
    data = response.json()
    if len(data["llm_conversation"]) <= 1:
        pytest.fail("Expected multiple LLM conversation entries, but found one or none.")
    if data["fixed_rule"] is None:
        pytest.fail("Expected a fixed rule in response, but none was found.")
