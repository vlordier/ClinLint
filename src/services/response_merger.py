def merge_responses(vale_results: list, llm_feedback: list) -> dict:
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
        raise TypeError("Inputs cannot be None")

    if not isinstance(vale_results, list) or not isinstance(llm_feedback, dict):
        raise TypeError("Invalid input types")

    # Validate Vale results structure
    for issue in vale_results:
        if not isinstance(issue, dict) or not all(
            k in issue for k in ["Line", "Message", "Rule"]
        ):
            raise ValueError("Invalid Vale result structure")

    # Validate LLM feedback structure
    if "feedback" not in llm_feedback:
        raise ValueError("Invalid LLM feedback structure")

    summary = (
        "No issues found."
        if not vale_results
        else f"{len(vale_results)} Vale issues detected; LLM provided suggestions."
    )

    return {
        "vale_issues": vale_results if vale_results else [],
        "llm_suggestions": llm_feedback["feedback"] if llm_feedback else [],
        "summary": summary if vale_results or llm_feedback else "No input provided.",
    }
