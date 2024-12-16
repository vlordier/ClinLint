import pytest
from app.services.response_merger import merge_responses

def test_merge_responses_basic(mock_vale_results):
    """Test basic response merging."""
    llm_feedback = {"feedback": ["Replace 'significant' with a specific term."]}
    result = merge_responses(mock_vale_results["stdin.md"], llm_feedback)
    assert "vale_issues" in result
    assert "llm_suggestions" in result
    assert "summary" in result
    assert len(result["vale_issues"]) == 2
    assert len(result["llm_suggestions"]) == 1

def test_merge_responses_empty_inputs():
    """Test merging empty inputs."""
    result = merge_responses([], {"feedback": []})
    assert result["vale_issues"] == []
    assert result["llm_suggestions"] == []
    assert "No issues found." in result["summary"]

def test_merge_responses_multiple_issues(mock_vale_results):
    """Test merging multiple issues."""
    llm_feedback = {"feedback": ["Improve clarity", "Add statistical details"]}
    result = merge_responses(mock_vale_results["stdin.md"], llm_feedback)
    assert len(result["vale_issues"]) == 2
    assert len(result["llm_suggestions"]) == 2

def test_merge_responses_invalid_input():
    """Test invalid input handling."""
    with pytest.raises(TypeError):
        merge_responses(None, {"feedback": []})
    with pytest.raises(TypeError):
        merge_responses([], None)
    with pytest.raises(ValueError):
        merge_responses([{"invalid": "structure"}], {"feedback": []})

def test_merge_responses_duplicate_feedback():
    """Test handling of duplicate feedback."""
    vale_results = [
        {"Line": 1, "Message": "Use specific metrics", "Rule": "CSR.Precision"},
        {"Line": 1, "Message": "Use specific metrics", "Rule": "CSR.Precision"}
    ]
    llm_feedback = {"feedback": ["Use specific metrics", "Use specific metrics"]}

    result = merge_responses(vale_results, llm_feedback)
    assert len(result["vale_issues"]) == 2  # Vale duplicates preserved
    assert len(result["llm_suggestions"]) == 1  # LLM duplicates deduplicated

def test_merge_responses_mixed_feedback_types():
    """Test handling of mixed feedback types."""
    vale_results = [{"Line": 1, "Message": "Test message", "Rule": "CSR.Test"}]
    llm_feedback = {
        "feedback": [
            "Simple string feedback",
            {"type": "suggestion", "text": "Complex feedback"},
            ["Nested", "feedback", "list"]
        ]
    }

    result = merge_responses(vale_results, llm_feedback)
    assert len(result["vale_issues"]) == 1
    assert len(result["llm_suggestions"]) == 3
    assert any(isinstance(s, str) for s in result["llm_suggestions"])
    assert any(isinstance(s, dict) for s in result["llm_suggestions"])
    assert any(isinstance(s, list) for s in result["llm_suggestions"])

def test_merge_responses_with_severity():
    """Test merging responses with severity levels."""
    vale_results = [
        {"Line": 1, "Message": "Critical issue", "Rule": "CSR.Critical", "Severity": "error"},
        {"Line": 2, "Message": "Minor issue", "Rule": "CSR.Minor", "Severity": "warning"}
    ]
    llm_feedback = {"feedback": ["Fix critical issue"]}

    result = merge_responses(vale_results, llm_feedback)
    assert len(result["vale_issues"]) == 2
    assert any(i.get("Severity") == "error" for i in result["vale_issues"])
    assert any(i.get("Severity") == "warning" for i in result["vale_issues"])

def test_merge_responses_large_input():
    """Test merging large number of responses."""
    vale_results = [
        {"Line": i, "Message": f"Issue {i}", "Rule": "CSR.Test"}
        for i in range(1000)
    ]
    llm_feedback = {"feedback": [f"Suggestion {i}" for i in range(1000)]}

    result = merge_responses(vale_results, llm_feedback)
    assert len(result["vale_issues"]) == 1000
    assert len(result["llm_suggestions"]) == 1000
