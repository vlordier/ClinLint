"""Manages configurations for Vale and LLM settings."""

import json
import logging
from pathlib import Path

from services.config import Config
from services.exceptions import ConfigurationError

logging.basicConfig(level=logging.INFO)
from typing import Any


class ConfigLoader:
    """Manages configurations for Vale and LLM settings.

    Provides cached access to configuration files with proper error handling.
    """

    def __init__(self, config_path: str = Config.CONFIG_PATH) -> None:
        """Initialize ConfigLoader with path to config file.

        Args:
            config_path: Path to the configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file contains invalid JSON
        """
        self.config_path = Path(config_path)  # Ensure the path is correctly set
        logging.info(f"Initializing ConfigLoader with config path: {config_path}")
        if not self.config_path.exists():
            logging.error(f"Configuration file not found at path: {config_path}")
            raise ConfigurationError(
                f"Configuration file not found at path: {config_path}"
            )  # Raise error if file doesn't exist
        self._load_config()

    def _load_config(self) -> None:
        """Load and validate the configuration file.

        Raises:
            ValueError: If config file contains invalid JSON
        """
        try:
            with open(self.config_path) as file:
                self.config = json.load(file)
            logging.info("Configuration loaded successfully.")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file: {e}")
            raise ConfigurationError(f"Invalid JSON in config file: {e}") from e

    def get_vale_config(self) -> dict[str, Any]:
        """Get Vale configuration settings.

        Returns:
            Dictionary containing Vale configuration
        """
        return self.config.get("vale", {})

    def get_llm_config(self) -> dict[str, Any]:
        """Get LLM configuration settings.

        Returns:
            Dictionary containing LLM configuration
        """
        return self.config.get("llm", {})

    def get_prompt_dir(self) -> str:
        """Get prompt templates directory path.

        Returns:
            Path to prompt templates directory
        """
        return self.config.get("prompt_dir", "src/services/prompts/")
