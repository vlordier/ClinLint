"""Model setup and configuration."""

import logging
import os
from typing import Optional

from langchain_openai import ChatOpenAI

from app.services.config import Config
from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ModelSetup:
    """Handles model initialization and configuration."""

    def __init__(self, config_dict: Optional[dict] = None):
        """Initialize model setup with configuration.

        Args:
            config_dict: Optional dictionary containing model configuration
        """
        try:
            self.config = Config(
                config_dict.get("config_path") if config_dict else None
            )
            self.provider = self.config.config.llm.provider
            logger.info(f"Initialized ModelSetup with provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize ModelSetup: {e}")
            logger.error(f"Failed to initialize ModelSetup: {e}")
            raise ConfigurationError(f"Model setup initialization failed: {e}") from e

    def get_model(self) -> ChatOpenAI:
        """Returns an LLM instance based on the configuration.

        Returns:
            ChatOpenAI: Configured model instance

        Raises:
            ConfigurationError: If model configuration is invalid
        """
        if self.provider == "openai":
            try:
                openai_config = self.config.config.llm.openai
                from services.config import (
                    DEFAULT_MAX_TOKENS,
                    DEFAULT_MODEL,
                    DEFAULT_TEMPERATURE,
                )

                return ChatOpenAI(
                    openai_api_key=openai_config.api_key.get_secret_value(),
                    model=openai_config.model or DEFAULT_MODEL,
                    temperature=openai_config.temperature or DEFAULT_TEMPERATURE,
                    max_tokens=openai_config.max_tokens or DEFAULT_MAX_TOKENS,
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI model: {e}")
                raise ConfigurationError(
                    f"OpenAI model initialization failed: {e}"
                ) from e
        else:
            raise ConfigurationError(f"Unsupported model provider: {self.provider}")

    def get_llm_template(self) -> dict:
        """Returns the LLM template based on the configuration."""
        if self.provider == "openai":
            return {
                "openai_api_key": os.getenv(
                    "OPENAI_API_KEY", self.config["openai"]["api_key"]
                ),
                "model": self.config["openai"]["model"],
                "temperature": self.config["openai"]["temperature"],
                "max_tokens": self.config["openai"]["max_tokens"],
            }
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")
