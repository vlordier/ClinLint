"""Configuration service module."""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from .exceptions import ConfigurationError
from .schemas.config_schema import AppConfig

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for the application."""

    # Default config path in the user's home directory
    CONFIG_PATH = os.path.expanduser("~/.config/clinlint/config.json")

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file and environment variables.

        Args:
            config_path: Path to config file, defaults to CONFIG_PATH env var

        Raises:
            ConfigurationError: If config is invalid or missing required values
        """
        self.config_path = config_path or os.getenv(
            "CONFIG_PATH", "config/default.json"
        )
        self._config: Optional[AppConfig] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration from file.

        Raises:
            ConfigurationError: If config file is invalid or missing
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise ConfigurationError(f"Config file not found: {self.config_path}")

            with open(config_file) as f:
                config_data = json.load(f)

            # Override with environment variables
            if os.getenv("OPENAI_API_KEY"):
                config_data["llm"]["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
            if os.getenv("MODEL_PROVIDER"):
                config_data["llm"]["provider"] = os.getenv("MODEL_PROVIDER")
            if os.getenv("PROMPT_DIR"):
                config_data["prompt_dir"] = os.getenv("PROMPT_DIR")
            if os.getenv("LOG_LEVEL"):
                config_data["log_level"] = os.getenv("LOG_LEVEL")

            self._config = AppConfig(**config_data)
            logger.info("Configuration loaded successfully")

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}") from e
        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}") from e

    @property
    def config(self) -> AppConfig:
        """Get the validated configuration.

        Returns:
            AppConfig: The validated configuration object

        Raises:
            ConfigurationError: If config is not loaded
        """
        if self._config is None:
            raise ConfigurationError("Configuration not loaded")
        return self._config
