"""Service for validating prompt templates."""

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.schemas.prompt_schemas import PromptTemplate, PromptValidationResult

logger = logging.getLogger(__name__)


class PromptValidator:
    """Validates prompt templates and their structure."""

    def validate_prompts_batch(
        self, prompt_dir: Path
    ) -> dict[str, PromptValidationResult]:
        """Validate all prompt templates in a directory.

        Args:
            prompt_dir: Directory containing prompt templates

        Returns:
            Dict mapping template names to validation results
        """
        results = {}
        if not prompt_dir.exists():
            logger.warning(f"Prompt directory not found: {prompt_dir}")
            return results

        for template_file in prompt_dir.glob("*.yaml"):
            try:
                with open(template_file) as f:
                    template_data = yaml.safe_load(f)
                result = self.validate_prompt(template_data)
                results[template_file.stem] = result
            except Exception as e:
                logger.error(f"Error processing template {template_file}: {e}")
                results[template_file.stem] = PromptValidationResult(
                    is_valid=False, errors=[f"Failed to process template: {str(e)}"]
                )

        return results

    def validate_prompt(self, template_data: dict) -> PromptValidationResult:
        """Validate a single prompt template."""
        result = PromptValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            template = PromptTemplate(**template_data)
            self._validate_template_content(template, result)
            self._validate_variables(template, result)
            self._check_common_issues(template, result.warnings)
            result.is_valid = not result.errors
        except ValidationError as e:
            result.errors.extend(str(err) for err in e.errors())
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def _validate_template_content(
        self, template: PromptTemplate, result: PromptValidationResult
    ) -> None:
        """Validate template content."""
        if len(template.template) > 2000:
            result.warnings.append(
                "Template exceeds recommended length of 2000 characters"
            )

    def _validate_variables(
        self, template: PromptTemplate, result: PromptValidationResult
    ) -> None:
        """Validate template variables."""
        template_vars = set(template.variables.keys())
        used_vars = self._extract_variables(template.template)

        # Check for undefined variables
        undefined = used_vars - template_vars
        if undefined:
            result.errors.append(
                f"Template references undefined variables: {', '.join(undefined)}"
            )

        # Check for unused variables
        unused = template_vars - used_vars
        if unused:
            result.warnings.append(
                f"Template has unused variables: {', '.join(unused)}"
            )

        # Validate variable types
        for var_name, var_def in template.variables.items():
            if var_def.required and var_def.default is not None:
                result.warnings.append(
                    f"Variable '{var_name}' is marked required but has a default value"
                )

            # Validate default value matches declared type
            if var_def.default is not None:
                try:
                    var_def.type.validate(var_def.default)
                except ValueError as e:
                    result.errors.append(
                        f"Default value for '{var_name}' does not match declared type: {e}"
                    )

    def _extract_variables(self, template: str) -> set[str]:
        """Extract variable names from template string."""
        import re

        return set(re.findall(r"\{(\w+)\}", template))

    def _check_common_issues(
        self, template: PromptTemplate, warnings: list[str]
    ) -> None:
        """Check for common template issues."""
        # Check for very short descriptions
        if len(template.description) < 10:
            warnings.append("Template description is very short")

        # Check for missing tags
        if not template.tags:
            warnings.append("Template has no tags")

        # Check for potential placeholder typos
        common_vars = {"text", "context", "input", "output"}
        used_vars = self._extract_variables(template.template)
        similar_vars = used_vars & common_vars
        if similar_vars:
            warnings.append(
                f"Template uses common variable names: {', '.join(similar_vars)}"
            )
