def merge_responses(vale_results: list, llm_feedback: dict) -> dict:
    """Merges Vale results and LLM feedback into a single response.

    Args:
        vale_results (list): Vale linting issues.
        llm_feedback (dict): Feedback from LLM.

    Returns:
        dict: Unified response combining Vale and LLM outputs.

    Raises:
        TypeError: If inputs are None or wrong type
        ValueError: If input structure is invalid
    """
    if vale_results is None or llm_feedback is None:
        raise TypeError("Inputs cannot be None") from None

    if not isinstance(vale_results, list):
        raise TypeError("vale_results must be a list") from None
    if not isinstance(llm_feedback, dict):
        raise TypeError("llm_feedback must be a dict") from None

    # Validate Vale results structure
    for issue in vale_results:
        if not isinstance(issue, dict) or not all(
            k in issue for k in ["Line", "Message", "Rule"]
        ):
            raise ValueError("Invalid Vale result structure") from None

    # Validate LLM feedback structure
    if "feedback" not in llm_feedback:
        raise ValueError("Invalid LLM feedback structure") from None

    summary = (
        "No issues found."
        if not vale_results
        else f"{len(vale_results)} Vale issues detected; LLM provided suggestions."
    )

    # Deduplicate LLM suggestions while preserving order
    llm_suggestions = []
    if llm_feedback and llm_feedback["feedback"]:
        seen = set()
        for suggestion in llm_feedback["feedback"]:
            suggestion_str = str(suggestion)
            if suggestion_str not in seen:
                seen.add(suggestion_str)
                llm_suggestions.append(suggestion)

    return {
        "vale_issues": vale_results if vale_results else [],
        "llm_suggestions": llm_suggestions,
        "summary": summary if vale_results or llm_feedback else "No input provided.",
    }
