import json
import os

from langchain_community.chat_models import ChatOpenAI


class ModelSetup:
    def __init__(self, config_path: str = "config/default.json"):
        with open(config_path) as file:
            self.config = json.load(file)
        self.provider = self.config.get("model_provider", "openai")

    def get_model(self):
        """Returns an LLM instance based on the configuration."""
        if self.provider == "openai":
            return ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY", self.config["openai"]["api_key"]),
                model=self.config["openai"]["model"],
                temperature=self.config["openai"]["temperature"],
                max_tokens=self.config["openai"]["max_tokens"],
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")

    def get_llm_template(self):
        """Returns the LLM template based on the configuration."""
        if self.provider == "openai":
            return {
                "openai_api_key": os.getenv("OPENAI_API_KEY", self.config["openai"]["api_key"]),
                "model": self.config["openai"]["model"],
                "temperature": self.config["openai"]["temperature"],
                "max_tokens": self.config["openai"]["max_tokens"],
            }
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")
