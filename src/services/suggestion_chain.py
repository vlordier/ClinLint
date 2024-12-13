from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from services.llm_judge import LLMJudge
from services.vale_runner import run_vale_on_text


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

    @validator('vale_rules', 'llm_templates', pre=True)
    def ensure_list(self, v): # noqa
        if v is None:
            return []
        return v

    @validator('mode')
    def validate_mode_requirements(self, v, values): # noqa
        if v == AnalysisMode.VALE_ONLY and not values.get('vale_rules'):
            raise ValueError("Vale rules required for VALE_ONLY mode")
        if v == AnalysisMode.LLM_ONLY and not values.get('llm_templates'):
            raise ValueError("LLM templates required for LLM_ONLY mode")
        return v

class SuggestionChain:
    """Flexible chain for generating suggestions using Vale and/or LLM analysis."""

    def __init__(self, vale_config: str, llm_judge: LLMJudge | None = None):
        """Initialize the suggestion chain with Vale configuration and LLM judge.

        Args:
            vale_config (str): Path to Vale configuration file.
            llm_judge (LLMJudge): Judge for LLM analysis.
        """
        self.vale_config = vale_config
        self.llm_judge = llm_judge

    def _run_vale_analysis(self, text: str, rules: list[str]) -> dict[str, Any]:
        """Run Vale analysis with specified rules.

        Args:
            text (str): Text to analyze.
            rules (list): Vale rules to apply.

        Returns:
            dict: Results of Vale analysis.
        """
        vale_results = run_vale_on_text(text, self.vale_config)
        vale_issues = [
            f"Line {issue['Line']}: {issue['Message']}"
            for _, issues in vale_results.items()
            for issue in issues
            if any(rule in issue.get('Rule', '') for rule in rules)
        ]
        return {
            "vale_issues": vale_results,
            "formatted_issues": "\n".join(vale_issues)
        }

    def _run_llm_analysis(self, text: str, templates: list[str], vale_issues: str | None = None) -> dict[str, Any]:
        """Run LLM analysis with specified templates."""
        if not self.llm_judge:
            raise ValueError("LLM judge not configured for LLM analysis")

        all_feedback = []
        for template in templates:
            prompt_data = {"text": text}
            if vale_issues:
                prompt_data["vale_issues"] = vale_issues

            feedback = self.llm_judge.get_feedback(template, **prompt_data)
            all_feedback.append(feedback)
        return {"feedback": all_feedback}

    def generate_suggestions(self, text: str, llm_template: Optional[str] = None, config: Optional[ChainConfig] = None) -> dict[str, Any]:
        """Generate suggestions based on configured analysis mode."""
        if isinstance(config, str):
            config = ChainConfig(mode=config)
        result = {}
        if config is None:
            config = llm_template  # Use llm_template as config if config is None
        if config.mode in [AnalysisMode.VALE_ONLY, AnalysisMode.COMBINED]:
            vale_analysis = self._run_vale_analysis(text, config.vale_rules or [])
            result['vale'] = vale_analysis

        if config.mode in [AnalysisMode.LLM_ONLY, AnalysisMode.COMBINED]:
            llm_analysis = self._run_llm_analysis(text, config.llm_templates or [], vale_analysis if config.mode == AnalysisMode.COMBINED else None)
            result['llm'] = llm_analysis

        return result
