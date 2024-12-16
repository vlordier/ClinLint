import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from app.schemas.prompt_schemas import PromptTemplate
from app.services.prompt_validator import PromptValidator

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages loading and caching of prompt templates.

    Provides efficient access to prompt templates with proper error handling.
    """

    def __init__(self, prompt_dir: str):
        """Initialize the prompt manager.

        Args:
            prompt_dir: Directory containing prompt templates

        Raises:
            FileNotFoundError: If prompt directory doesn't exist
        """
        self.prompt_dir = Path(prompt_dir)
        if not self.prompt_dir.exists():
            raise FileNotFoundError(f"Prompt directory not found: {prompt_dir}")

        self.validator = PromptValidator()
        self._templates: dict[str, PromptTemplate] = {}
        self._load_all_templates()

    def _load_all_templates(self) -> None:
        """Load and validate all templates in the prompt directory."""
        validation_results = self.validator.validate_prompts_batch(self.prompt_dir)

        for template_name, result in validation_results.items():
            if result.is_valid:
                try:
                    template_path = self.prompt_dir / f"{template_name}.yaml"
                    with open(template_path) as f:
                        template_data = yaml.safe_load(f)
                    self._templates[template_name] = PromptTemplate(**template_data)
                except Exception as e:
                    logger.error(f"Error loading template {template_name}: {e}")
            else:
                logger.warning(
                    f"Template {template_name} validation failed: {result.errors}"
                )

    def get_prompt_template(self, template_name: str, refresh_cache: bool = False) -> Optional[PromptTemplate]:
        """Load and cache a prompt template.

        Args:
            template_name: Name of the template file (without .yaml extension)
            refresh_cache: Force reload template from disk

        Returns:
            Validated PromptTemplate instance

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template file is invalid
        """
        if refresh_cache or template_name not in self._templates:
            template_path = self.prompt_dir / f"{template_name}.yaml"
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")

            try:
                with open(template_path) as f:
                    template_data = yaml.safe_load(f)
                if not template_data:
                    raise ValueError(f"Empty template file: {template_path}")

                # Validate template data structure
                required_fields = ["name", "description", "template"]
                missing_fields = [f for f in required_fields if f not in template_data]
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")

                template = PromptTemplate(**template_data)

                # Validate template content
                result = self.validator.validate_prompt(template_data)
                if not result.is_valid:
                    raise ValueError(f"Invalid template: {', '.join(result.errors)}")

                self._templates[template_name] = template
                logger.info(f"Loaded and cached template: {template_name}")

            except yaml.YAMLError as e:
                logger.error(f"YAML error in template {template_name}: {e}")
                return None
            except ValidationError as e:
                logger.error(f"Validation error in template {template_name}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error loading template {template_name}: {e}")
                return None
            finally:
                # Clear cache on error
                if template_name in self._templates:
                    del self._templates[template_name]

        return self._templates[template_name]

    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get just the template content string."""
        try:
            template = self.get_prompt_template(template_name)
            return template.template
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error getting template content: {e}")
            return None

    def validate_template(self, template_name: str) -> bool:
        """Validate a specific template.

        Args:
            template_name: Name of template to validate

        Returns:
            True if template is valid, False otherwise
        """
        try:
            template_path = self.prompt_dir / f"{template_name}.yaml"
            if not template_path.exists():
                return False

            with open(template_path) as f:
                template_data = yaml.safe_load(f)
            result = self.validator.validate_prompt(template_data)
            return result.is_valid
        except Exception as e:
            logger.error(f"Error validating template {template_name}: {e}")
            return False

    def list_templates(self) -> dict[str, PromptTemplate]:
        """Get all valid templates.

        Returns:
            Dict mapping template names to PromptTemplate instances
        """
        return self._templates.copy()
