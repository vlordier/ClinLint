from fastapi import FastAPI
from pydantic import BaseModel
from services.suggestion_chain import SuggestionChain
from services.llm_judge import LLMJudge

app = FastAPI()

class SuggestionInput(BaseModel):
    text: str
    vale_config: str
    llm_template: str

class BatchInput(BaseModel):
    texts: list[SuggestionInput]

@app.post("/suggestions")
def get_suggestions(input: SuggestionInput):
    """
    Endpoint to generate suggestions for improving a single text.
    """
    llm_judge = LLMJudge("v1")
    suggestion_chain = SuggestionChain(input.vale_config, llm_judge)
    return suggestion_chain.generate_suggestions(input.text, input.llm_template)

@app.post("/suggestions/batch")
def get_batch_suggestions(input: BatchInput):
    """
    Endpoint to generate suggestions for improving multiple texts in batch.
    """
    llm_judge = LLMJudge("v1")
    suggestion_chain = SuggestionChain(input.texts[0].vale_config, llm_judge)
    results = []
    for text_input in input.texts:
        result = suggestion_chain.generate_suggestions(text_input.text, text_input.llm_template)
        results.append(result)
    return {"results": results}
