import pytest

from services.response_merger import merge_responses


def test_merge_responses_basic():
    vale_results = [{"Line": 1, "Message": "Avoid vague terms like 'significant'.", "Rule": "CSR.Vagueness"}]
    llm_feedback = {"feedback": ["Replace 'significant' with a specific term."]}

    result = merge_responses(vale_results, llm_feedback)
    assert "vale_issues" in result
    assert "llm_suggestions" in result
    assert "summary" in result
    assert len(result["vale_issues"]) == 1
    assert len(result["llm_suggestions"]) == 1

def test_merge_responses_empty_inputs():
    result = merge_responses([], {"feedback": []})
    assert result["vale_issues"] == []
    assert result["llm_suggestions"] == []
    assert "No issues found." in result["summary"]

def test_merge_responses_multiple_issues():
    vale_results = [
        {"Line": 1, "Message": "Use 'subject' instead of 'patient'.", "Rule": "CSR.Terminology"},
        {"Line": 2, "Message": "Avoid abbreviations.", "Rule": "CSR.Abbreviations"}
    ]
    llm_feedback = {"feedback": ["Improve clarity", "Add statistical details"]}

    result = merge_responses(vale_results, llm_feedback)
    assert len(result["vale_issues"]) == 2
    assert len(result["llm_suggestions"]) == 2

def test_merge_responses_invalid_input():
    with pytest.raises(ValueError):
        merge_responses(None, {"feedback": []})
    with pytest.raises(ValueError):
        merge_responses([], None)
