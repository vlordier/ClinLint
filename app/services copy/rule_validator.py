"""Service for validating Vale rules."""

import logging
from typing import Optional

from pydantic import ValidationError
from schemas.vale.vale_package_schema import RuleDefinition
from services.llm_feedback import LLMFeedback

logger = logging.getLogger(__name__)


class RuleValidator:
    """Handles Vale rule validation and LLM-assisted fixes."""

    def __init__(self, llm_feedback: Optional[LLMFeedback] = None):
        """Initialize validator with optional LLM feedback."""
        self.llm_feedback = llm_feedback

    def validate_rules_batch(
        self, rules: list[RuleDefinition], use_llm: bool = False, max_attempts: int = 3
    ) -> list[dict]:
        """Validate multiple rules in batch and optionally get LLM fixes.

        Args:
            rules: List of rule definitions to validate
            use_llm: Whether to use LLM for fixes
            max_attempts: Maximum LLM fix attempts per rule

        Returns:
            List of validation results for each rule
        """
        return [self.validate_rule(rule, use_llm, max_attempts) for rule in rules]

    def validate_rule(
        self, rule: RuleDefinition, use_llm: bool = False, max_attempts: int = 3
    ) -> dict:
        """Validate a rule and optionally get LLM fixes.

        Args:
            rule: Rule definition to validate
            use_llm: Whether to use LLM for fixes
            max_attempts: Maximum LLM fix attempts

        Returns:
            dict containing validation results
        """
        logger.info(f"Validating rule: {rule.dict()}")

        validation_result = {
            "is_valid": True,
            "errors": [],
            "fixed_rule": None,
            "llm_conversation": [],
        }

        try:
            RuleDefinition(**rule.dict())
        except ValidationError as e:
            logger.warning(f"Rule validation failed: {str(e)}")
            validation_result["is_valid"] = False
            validation_result["errors"] = [str(err) for err in e.errors()]

            if use_llm and self.llm_feedback:
                validation_result.update(
                    self._get_llm_fixes(rule, validation_result["errors"], max_attempts)
                )

        return validation_result

    def create_and_save_rule(self, rule_data: dict, save_path: str) -> dict:
        """Create a new rule, validate it, and save if valid.

        Args:
            rule_data: Dictionary containing rule definition
            save_path: Path to save the valid rule

        Returns:
            dict containing validation results and save status
        """
        try:
            # Create a RuleDefinition instance
            rule = RuleDefinition(**rule_data)
            validation_result = self.validate_rule(rule)

            if validation_result["is_valid"]:
                # Save the rule to the specified path
                with open(save_path, 'w') as file:
                    file.write(rule.json(indent=4))
                validation_result["save_status"] = "Rule saved successfully"
            else:
                validation_result["save_status"] = "Rule not saved due to validation errors"

            return validation_result

        except ValidationError as e:
            logger.error(f"Error creating rule: {str(e)}")
            return {
                "is_valid": False,
                "errors": [str(err) for err in e.errors()],
                "save_status": "Rule not saved due to creation errors"
            }
    def _get_llm_fixes(
        self, rule: RuleDefinition, errors: list[str], max_attempts: int
    ) -> dict:
        """Get LLM suggestions for fixing rule errors.

        Args:
            rule: Invalid rule definition
            errors: Validation errors
            max_attempts: Maximum fix attempts

        Returns:
            dict with fix results
        """
        conversation_history = []

        for attempt in range(max_attempts):
            try:
                feedback = self.llm_feedback.get_feedback(
                    "rule_validation_prompt",
                    rule=rule.dict(),
                    error=errors,
                    history="\n".join(conversation_history),
                )

                if "suggested_rule" in feedback:
                    try:
                        fixed_rule = RuleDefinition(**feedback["suggested_rule"])
                        return {
                            "fixed_rule": fixed_rule.dict(),
                            "is_valid": True,
                            "llm_conversation": conversation_history,
                        }
                    except ValidationError as ve:
                        conversation_history.append(
                            f"Attempt {attempt + 1} failed: {str(ve)}"
                        )
                else:
                    conversation_history.append(
                        f"Attempt {attempt + 1}: No valid suggestion"
                    )

            except Exception as e:
                conversation_history.append(f"Attempt {attempt + 1} error: {str(e)}")
                logger.error(f"LLM fix attempt failed: {str(e)}")

        return {"fixed_rule": None, "llm_conversation": conversation_history}
