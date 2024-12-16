"""FastAPI application for text analysis and suggestion generation."""

import logging

# from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from pydantic import BaseModel, Field
from app.routers import (
    health,
    rules,
    search,
    suggestions,
    validate,
    vocabularies,
)

# from app.schemas.vale_schemas import ValeVocabulary
from app.services.config import Config

# from app.services.suggestion_chain import AnalysisMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClinLint API",
    description="API for clinical document analysis and suggestions",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global config
config = Config()

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(rules.router, prefix="/rules", tags=["Rules"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(suggestions.router, prefix="/suggestions", tags=["Suggestions"])
app.include_router(validate.router, prefix="/validate", tags=["Validation"])
app.include_router(vocabularies.router, prefix="/vocabularies", tags=["Vocabularies"])



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)








































