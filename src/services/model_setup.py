import json
import os

from langchain_community.chat_models import ChatOpenAI

from services.config import Config


class ModelSetup:
    def __init__(self, config_path: str = "config/default.json"):
        if isinstance(config_path, dict):
            self.config = config_path
        else:
            with open(config_path) as file:
                self.config = json.load(file)
        self.provider = Config.MODEL_PROVIDER

    def get_model(self) -> ChatOpenAI:
        """Returns an LLM instance based on the configuration."""
        if self.provider == "openai":
            return ChatOpenAI(
                openai_api_key=Config.OPENAI_API_KEY
                or self.config.get("openai", {}).get("api_key"),
                model=self.config["openai"]["model"],
                temperature=self.config["openai"]["temperature"],
                max_tokens=self.config["openai"]["max_tokens"],
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")

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
