from services.vale_runner import run_vale_on_text
from services.llm_judge import LLMJudge

class SuggestionChain:
    """
    Chains Vale results with LLM feedback to suggest text improvements.
    """

    def __init__(self, vale_config: str, llm_judge: LLMJudge):
        self.vale_config = vale_config
        self.llm_judge = llm_judge

    def generate_suggestions(self, text: str, llm_template: str) -> dict:
        """
        Chains Vale output and LLM feedback for suggestions.
        """
        # Step 1: Vale Linting
        vale_results = run_vale_on_text(text, self.vale_config)
        vale_issues = [
            f"Line {issue['Line']}: {issue['Message']}"
            for _, issues in vale_results.items()
            for issue in issues
        ]
        vale_issues_str = "\n".join(vale_issues)

        # Step 2: LLM Feedback
        prompt_data = {"vale_issues": vale_issues_str, "text": text}
        llm_feedback = self.llm_judge.get_feedback("", llm_template, **prompt_data)

        return {
            "vale_issues": vale_results,
            "suggestions": llm_feedback["feedback"]
        }
