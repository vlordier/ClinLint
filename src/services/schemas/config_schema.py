"""Configuration schemas for the application."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr


class OpenAIConfig(BaseModel):
    """OpenAI-specific configuration settings."""

    api_key: SecretStr = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-3.5-turbo", description="Model name to use")
    temperature: float = Field(
        default=0.7, ge=0, le=1, description="Sampling temperature"
    )
    max_tokens: int = Field(default=500, gt=0, description="Maximum tokens to generate")


class LLMConfig(BaseModel):
    """Language model configuration settings."""

    provider: Literal["openai"] = Field(default="openai", description="LLM provider")
    openai: Optional[OpenAIConfig] = None


class ValeConfig(BaseModel):
    """Vale linter configuration settings."""

    config_path: str = Field(..., description="Path to Vale config file")
    styles_path: str = Field(..., description="Path to Vale styles")


class AppConfig(BaseModel):
    """Main application configuration."""

    llm: LLMConfig
    vale: ValeConfig
    prompt_dir: str = Field(
        default="src/services/prompts/", description="Prompt templates directory"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
