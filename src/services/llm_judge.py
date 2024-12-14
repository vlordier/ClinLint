import logging

import yaml

logging.basicConfig(level=logging.INFO)
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from services.exceptions import AnalysisError, ConfigurationError

from .model_setup import ModelSetup


class LLMJudge:
    """Provides LLM-based reasoning to suggest text improvements."""

    def __init__(self, version: str, config_loader):
        """Initialize LLMJudge with configuration.

        Args:
            version: Version identifier
            config_loader: Configuration loader instance
        """
        try:
            self.model = ModelSetup(config_loader.get_llm_config()).get_model()
            self.prompt_dir = config_loader.get_prompt_dir()
            logging.info("LLMJudge initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize LLMJudge: {e}")
            raise ConfigurationError(f"LLMJudge initialization failed: {e}")

    def get_feedback(self, text: str, prompt_template: str, **kwargs) -> dict:
        """Generate feedback for a single text using LLM."""
        prompt = self.load_prompt(prompt_template)
        # Create a chain with the model and prompt
        try:
            chain = LLMChain(llm=self.model, prompt=prompt)
        except Exception as e:
            logging.error("Failed to create LLMChain.")
            raise AnalysisError("Error in LLMChain setup.") from e
        return {"feedback": chain.run(text=text, **kwargs)}

    def load_prompt(self, template_name: str) -> PromptTemplate:
        """Load a prompt template."""
        try:
            with open(f"{self.prompt_dir}/{template_name}.yaml") as file:
                template = yaml.safe_load(file)
            logging.info(f"Loaded prompt template: {template_name}")
        except FileNotFoundError:
            logging.error(f"Prompt template file not found: {template_name}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML for template {template_name}: {e}")
            raise ValueError(f"Invalid YAML in template {template_name}") from e
        return PromptTemplate(template=template["template"])
