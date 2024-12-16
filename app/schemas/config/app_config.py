from typing import Literal

from pydantic import BaseModel, Field

from .llm_config import LLMConfig
from .vale_config import ValeConfig


class AppConfig(BaseModel):
    """Main application configuration."""

    llm: LLMConfig
    vale: ValeConfig
    prompt_dir: str = Field(
        default="prompts/", description="Prompt templates directory"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
