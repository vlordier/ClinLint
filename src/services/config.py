import os


class Config:
    """Configuration management for environment variables and settings."""

    CONFIG_PATH = os.getenv("CONFIG_PATH", "config/default.json")
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    PROMPT_DIR = os.getenv("PROMPT_DIR", "src/services/prompts/")
    LLM_JUDGE_VERSION = os.getenv("LLM_JUDGE_VERSION", "v1")
