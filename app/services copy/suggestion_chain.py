import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.services.exceptions import AnalysisError
from app.services.llm_feedback import LLMFeedback
from app.services.vale_config_manager import ValeConfigManager
from app.services.vale_runner import run_vale_on_text

logging.basicConfig(level=logging.INFO)


class AnalysisMode(str, Enum):
    """Modes for suggestion chain analysis."""

    VALE_ONLY = "vale_only"
    LLM_ONLY = "llm_only"
    COMBINED = "combined"


class ChainConfig(BaseModel):
    """Configuration for the suggestion chain."""

    mode: AnalysisMode
    vale_rules: list[str] | None = Field(default_factory=list)
    llm_templates: list[str] | None = Field(default_factory=list)
    section_name: str | None = None


class SuggestionChain:
    """Flexible chain for generating suggestions using Vale and/or LLM analysis."""

    def __init__(
        self, vale_config: str | None = None, llm_feedback: LLMFeedback | None = None
    ):
        """Initialize the suggestion chain with Vale configuration and LLM feedback.

        Args:
            vale_config: Optional path to Vale configuration file
            llm_feedback: Optional LLM feedback instance

        Raises:
            ValueError: If vale_config is None or llm_feedback is invalid
        """
        if vale_config is None:
            raise ValueError("Invalid Vale configuration path.")

        self.vale_config = vale_config
        self.vale_manager = ValeConfigManager()

        if llm_feedback and not isinstance(llm_feedback, LLMFeedback):
            raise ValueError("Invalid LLMFeedback instance.")
        self.llm_judge = llm_feedback  # Renamed for consistency with usage

    def _run_vale_analysis(self, text: str, rules: list[str]) -> dict[str, Any]:
        """Run Vale analysis with specified rules.

        Args:
            text (str): Text to analyze.
            rules (list): Vale rules to apply.

        Returns:
            dict: Results of Vale analysis.
        """
        # Run Vale analysis and filter issues based on specified rules
        try:
            if not text.strip():
                return {"vale_issues": {"stdin.md": []}, "formatted_issues": ""}

            vale_results = run_vale_on_text(text, self.vale_config)
            logging.info("Vale analysis completed successfully.")
        except ValueError as e:
            logging.error("Error during Vale analysis.")
            raise AnalysisError("Vale analysis failed.") from e
        vale_issues = [
            f"Line {issue['Line']}: {issue['Message']}"
            for _, issues in vale_results.items()
            for issue in issues
            if any(rule in issue.get("Rule", "") for rule in rules)
        ]
        return {"vale_issues": vale_results, "formatted_issues": "\n".join(vale_issues)}

    def _run_llm_analysis(
        self, text: str, templates: list[str], vale_issues: str | None = None
    ) -> dict[str, Any]:
        """Run LLM analysis with specified templates."""
        # Ensure LLM judge is configured before running analysis
        if not self.llm_judge:
            logging.error("LLM judge not configured for LLM analysis.")
            raise ValueError("LLM judge not configured for LLM analysis")

        all_feedback = []
        # Run LLM analysis using the provided templates
        try:
            for template in templates:
                prompt_data = {"text": text}
                if vale_issues:
                    prompt_data["vale_issues"] = vale_issues

                feedback = self.llm_judge.get_feedback(template, **prompt_data)
                all_feedback.append(feedback)
        except Exception as e:
            logging.error(f"Error during LLM analysis: {e}")
            logging.error("Error during LLM analysis.")
            raise AnalysisError("LLM analysis failed.") from e

        return {"feedback": all_feedback}

    def generate_suggestions(
        self,
        text: str,
        llm_template: Optional[str] = None,
        config: Optional[ChainConfig] = None,
    ) -> dict[str, Any]:
        """Generate suggestions based on configured analysis mode."""
        # Ensure the configuration is properly initialized
        if isinstance(config, str):
            logging.warning("Config passed as string, initializing ChainConfig.")
            config = ChainConfig(mode=config)
        result = {}
        if config is None:
            if llm_template is not None:
                logging.warning("Config is None, using llm_template as config.")
                config = (
                    llm_template
                    if isinstance(llm_template, ChainConfig)
                    else ChainConfig(mode=AnalysisMode.LLM_ONLY)
                )
            else:
                logging.warning("No config provided, using default LLM_ONLY mode")
                config = ChainConfig(mode=AnalysisMode.LLM_ONLY)

        if config.mode in [AnalysisMode.VALE_ONLY, AnalysisMode.COMBINED]:
            vale_analysis = self._run_vale_analysis(text, config.vale_rules or [])
            result["vale"] = vale_analysis

        if config.mode in [AnalysisMode.LLM_ONLY, AnalysisMode.COMBINED]:
            llm_analysis = self._run_llm_analysis(
                text,
                config.llm_templates or [],
                vale_analysis["formatted_issues"]
                if config.mode == AnalysisMode.COMBINED
                else None,
            )
            result["llm"] = llm_analysis

        # Merge and deduplicate results
        if result:
            vale_results = result.get('vale', {}).get('vale_issues', [])
            llm_feedback = result.get('llm', {}).get('feedback', [])

            # Deduplicate LLM suggestions while preserving order
            seen = set()
            llm_suggestions = []
            if llm_feedback:
                for suggestion in llm_feedback[:100]:  # Limit to 100 suggestions
                    suggestion_str = str(suggestion)
                    if suggestion_str not in seen:
                        seen.add(suggestion_str)
                        llm_suggestions.append(suggestion)

            summary = (
                "No issues found."
                if not vale_results
                else f"{len(vale_results)} Vale issues detected; LLM provided suggestions."
            )

            result['merged'] = {
                'vale_issues': vale_results if vale_results else [],
                'llm_suggestions': llm_suggestions,
                'summary': summary if vale_results or llm_feedback else "No input provided.",
            }

        return result
