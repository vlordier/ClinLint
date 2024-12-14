"""FastAPI application for text analysis and suggestion generation."""

import os

from fastapi import FastAPI
from pydantic import BaseModel

from services.config_loader import ConfigLoader
from services.llm_judge import LLMJudge
from services.suggestion_chain import SuggestionChain

from .services.config import Config

app = FastAPI()

config = Config()  # Initialize global config


class SuggestionInput(BaseModel):
    """Input model for single text analysis request."""

    text: str
    vale_config: str
    llm_template: str


class BatchInput(BaseModel):
    """Input model for batch text analysis request."""

    texts: list[SuggestionInput]


@app.post("/suggestions")
def get_suggestions(suggestion_input: SuggestionInput) -> dict:
    """Generate suggestions for improving a single text."""
    config_loader = ConfigLoader(config.config_path)
    llm_judge = LLMJudge("v1", config_loader)
    suggestion_chain = SuggestionChain(suggestion_input.vale_config, llm_judge)
    return suggestion_chain.generate_suggestions(
        suggestion_input.text, suggestion_input.llm_template
    )


@app.post("/suggestions/batch")
def get_batch_suggestions(batch_input: BatchInput) -> dict:
    """Generate suggestions for improving multiple texts in batch."""
    config_loader = ConfigLoader()
    llm_judge = LLMJudge(os.getenv("LLM_JUDGE_VERSION", "v1"), config_loader)
    suggestion_chain = SuggestionChain(batch_input.texts[0].vale_config, llm_judge)
    results = []
    for text_input in batch_input.texts:
        result = suggestion_chain.generate_suggestions(
            text_input.text, text_input.llm_template
        )
        results.append(result)
    return {"results": results}
