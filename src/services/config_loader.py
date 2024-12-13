import json

class ConfigLoader:
    """
    Manages configurations for Vale and LLM settings.
    """

    def __init__(self, config_path: str = "config/default.json"):
        with open(config_path, "r") as file:
            self.config = json.load(file)

    def get_vale_config(self):
        return self.config.get("vale", {})

    def get_llm_config(self):
        return self.config.get("llm", {})

    def get_prompt_dir(self):
        return self.config.get("prompt_dir", "src/services/prompts/")
