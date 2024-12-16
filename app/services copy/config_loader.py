"""Manages configurations for Vale and LLM settings.

This module provides functionality to load and manage configuration settings
for Vale and LLM (Large Language Model) services. It ensures that configurations
are loaded from a specified file and provides access to different configuration
sections.
"""

import json
import logging
from pathlib import Path
from typing import Any

from services.config import Config
from services.exceptions import ConfigurationError

logging.basicConfig(level=logging.INFO)


def get_config_loader(config_path: str = Config.CONFIG_PATH) -> 'ConfigLoader':
    """Dependency to get a ConfigLoader instance."""
    return ConfigLoader(config_path)


class ConfigLoader:
    """Initialize ConfigLoader with path to config file.

    Args:
        config_path: Path to the configuration file

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file contains invalid JSON
    """

    def __init__(self, config_path: str = Config.CONFIG_PATH) -> None:
        """Initialize ConfigLoader with path to config file.

        Args:
            config_path: Path to the configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file contains invalid JSON
        """
        self.config_path = Path(config_path)
        logging.debug(f"Initializing ConfigLoader with config path: {self.config_path}")

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            self._initialize_default_config()

        self._load_config()

    def _initialize_default_config(self) -> None:
        """Initialize configuration file with default settings."""
        default_config_path = Path(__file__).parent.parent / "config" / "default_config.json"
        try:
            with open(default_config_path) as f:
                default_config = json.load(f)

            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logging.info(f"Initialized default configuration at: {self.config_path}")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise ConfigurationError(f"Failed to initialize default configuration: {e}")

    def _load_config(self) -> None:
        """Load and validate the configuration file.

        Raises:
            ValueError: If config file contains invalid JSON
        """
        try:
            with open(self.config_path) as file:
                self.config = json.load(file)
            logging.debug("Configuration loaded successfully.")
        except json.JSONDecodeError as e:
            logging.error(
                f"Invalid JSON in config file: {e}. Please check the file format."
            )
            raise ConfigurationError(f"Invalid JSON in config file: {e}") from e

    def get_config_section(self, section: str, default: Any = None) -> Any:
        """Get configuration section.

        Args:
            section: Configuration section name
            default: Default value if section not found

        Returns:
            Configuration section contents

        Raises:
            ConfigurationError: If section not found and no default provided
        """
        if section not in self.config and default is None:
            raise ConfigurationError(f"Configuration section '{section}' not found")
        return self.config.get(section, default or {})

    def get_vale_config(self) -> dict[str, Any]:
        """Get Vale configuration settings."""
        return self.get_config_section("vale")

    def get_llm_config(self) -> dict[str, Any]:
        """Get LLM configuration settings."""
        return self.get_config_section("llm")

    def get_prompt_dir(self) -> str:
        """Get prompt templates directory path."""
        return self.get_config_section("prompt_dir", "prompts/")
