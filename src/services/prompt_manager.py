from functools import lru_cache
from pathlib import Path

import yaml


class PromptManager:
    """Manages loading and caching of prompt templates.

    Provides efficient access to prompt templates with proper error handling.
    """

    def __init__(self, prompt_dir: str):
        self.prompt_dir = Path(prompt_dir)
        if not self.prompt_dir.exists():
            raise FileNotFoundError(f"Prompt directory not found: {prompt_dir}")

    @lru_cache(maxsize=32) # noqa
    def get_prompt_template(self, template_name: str) -> dict:
        """Load and cache a prompt template.

        Args:
            template_name: Name of the template file (without .yaml extension)

        Returns:
            Dict containing the template configuration

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template file is invalid
        """
        template_path = self.prompt_dir / f"{template_name}.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        try:
            with open(template_path) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid template YAML: {e}") from e

    def get_template_content(self, template_name: str) -> str | None:
        """Get just the template content string."""
        template = self.get_prompt_template(template_name)
        return template.get("template")
