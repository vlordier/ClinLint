"""Module for LLM-based feedback generation."""

import logging
from pathlib import Path

import yaml
from langchain.chains import LLMChain
from schemas.prompt.prompt_schemas import PromptTemplate
from services.exceptions import AnalysisError, ConfigurationError
from services.model_setup import ModelSetup


class LLMFeedback:
    """Provides LLM-based reasoning to suggest text improvements."""

    def __init__(self, version: str, config_loader):
        """Initialize LLMFeedback with configuration.

        Args:
            version: Version identifier
            config_loader: Configuration loader instance
        """
        try:
            config = config_loader.get_llm_config()
            self._model = ModelSetup(config).get_model()
            self.prompt_dir = config_loader.get_prompt_dir()
            logging.info(
                "LLMFeedback initialized successfully with model: %s",
                config.get("openai", {}).get("model", "unknown"),
            )
            logging.debug("Prompt directory set to: %s", self.prompt_dir)
        except Exception as e:
            logging.exception("Failed to initialize LLMFeedback")
            raise ConfigurationError(f"LLMFeedback initialization failed: {e}") from e

    def get_feedback(self, text: str, prompt_template: str, **kwargs) -> dict:
        """Generate feedback for a single text using LLM.

        Args:
            text: Input text to analyze
            prompt_template: Name of prompt template to use
            **kwargs: Additional template variables

        Returns:
            dict containing feedback from LLM

        Raises:
            AnalysisError: If feedback generation fails
            ValueError: If inputs are invalid
        """
        if not text or not prompt_template:
            raise ValueError("Text and prompt_template must not be empty")

        logging.debug("Loading prompt template: %s", prompt_template)
        try:
            prompt = self.load_prompt(prompt_template)
            logging.debug("Prompt loaded successfully: %s", prompt_template)

            from concurrent.futures import ThreadPoolExecutor
            from concurrent.futures import TimeoutError as FuturesTimeoutError
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: LLMChain(llm=self._model, prompt=prompt).run(text=text, **kwargs))
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                except FuturesTimeoutError:
                    raise AnalysisError("LLM request timed out after 30 seconds") from None

            if not result:
                raise AnalysisError("LLM returned empty response")

            return {"feedback": result}
        except Exception as e:
            logging.error("Failed to generate LLM feedback: %s", e)
            raise AnalysisError(f"Error generating LLM feedback: {str(e)}") from e

    def load_prompt(self, template_name: str) -> PromptTemplate:
        """Load a prompt template.

        Args:
            template_name: Name of template to load

        Returns:
            Loaded prompt template

        Raises:
            FileNotFoundError: If template file not found
            ValueError: If template YAML is invalid
        """
        try:
            prompt_path = Path(self.prompt_dir) / "prompts" / f"{template_name}.yaml"
            with open(prompt_path) as file:
                template = yaml.safe_load(file)
            logging.info(f"Loaded prompt template: {template_name}")
        except FileNotFoundError:
            logging.error(f"Prompt template file not found: {template_name}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML for template {template_name}: {e}")
            raise ValueError(f"Invalid YAML in template {template_name}") from e
        return PromptTemplate(template=template["template"])
