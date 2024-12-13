def merge_responses(vale_results, llm_feedback):
    """Merges Vale results and LLM feedback into a single response.

    Args:
        vale_results (list): Vale linting issues.
        llm_feedback (dict): Feedback from LLM.

    Returns:
        dict: Unified response combining Vale and LLM outputs.
    """
    return {
        "vale_issues": vale_results,
        "llm_suggestions": llm_feedback,
        "summary": f"{len(vale_results)} Vale issues detected; LLM provided suggestions.",
    }
