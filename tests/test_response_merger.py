from services.response_merger import merge_responses

def test_merge_responses():
    vale_results = [{"Line": 1, "Message": "Avoid vague terms like 'significant'."}]
    llm_feedback = {"feedback": "Replace 'significant' with a specific term."}

    result = merge_responses(vale_results, llm_feedback)
    assert "vale_issues" in result
    assert "llm_suggestions" in result
    assert "summary" in result