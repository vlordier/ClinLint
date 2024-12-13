"""FastAPI application for text analysis and suggestion generation."""

from fastapi import FastAPI
from pydantic import BaseModel

from src.services.llm_judge import LLMJudge
from src.services.suggestion_chain import SuggestionChain

app = FastAPI()

class SuggestionInput(BaseModel):
    """Input model for single text analysis request."""
    text: str
    vale_config: str
    llm_template: str

class BatchInput(BaseModel):
    """Input model for batch text analysis request."""
    texts: list[SuggestionInput]

@app.post("/suggestions")
def get_suggestions(suggestion_input: SuggestionInput):
    """Generate suggestions for improving a single text."""
    llm_judge = LLMJudge("v1")
    suggestion_chain = SuggestionChain(suggestion_input.vale_config, llm_judge)
    return suggestion_chain.generate_suggestions(input.text, input.llm_template)

@app.post("/suggestions/batch")
def get_batch_suggestions(batch_input: BatchInput):
    """Generate suggestions for improving multiple texts in batch."""
    llm_judge = LLMJudge("v1")
    suggestion_chain = SuggestionChain(batch_input.texts[0].vale_config, llm_judge)
    results = []
    for text_input in input.texts:
        result = suggestion_chain.generate_suggestions(text_input.text, text_input.llm_template)
        results.append(result)
    return {"results": results}
