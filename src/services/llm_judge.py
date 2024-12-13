import yaml
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from .model_setup import ModelSetup


class LLMJudge:
    """Provides LLM-based reasoning to suggest text improvements."""

    def __init__(self, version: str, config_loader):
        self.model = ModelSetup(config_loader.get_llm_config()).get_model()
        self.prompt_dir = config_loader.get_prompt_dir()

    def get_feedback(self, text: str, prompt_template: str, **kwargs) -> dict:
        """Generate feedback for a single text using LLM."""
        prompt = self.load_prompt(prompt_template)
        chain = LLMChain(llm=self.model, prompt=prompt)
        return {"feedback": chain.run(text=text, **kwargs)}

    def load_prompt(self, template_name: str) -> PromptTemplate:
        """Load a prompt template."""
        with open(f"{self.prompt_dir}/{template_name}.yaml") as file:
            template = yaml.safe_load(file)
        return PromptTemplate(template=template["template"])
