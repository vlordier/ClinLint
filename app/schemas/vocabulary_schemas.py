"""Schema definitions for Vale vocabularies."""

from pydantic import BaseModel, Field
from typing import Optional

class VocabularyTerms(BaseModel):
    """Schema for vocabulary terms."""
    accept: list[str] = Field(default_factory=list, description="Accepted terms")
    reject: list[str] = Field(default_factory=list, description="Rejected terms")

class Vocabulary(BaseModel):
    """Schema for a complete vocabulary."""
    name: str = Field(..., description="Vocabulary name")
    terms: VocabularyTerms = Field(..., description="Vocabulary terms")
    description: Optional[str] = Field(None, description="Vocabulary description")
    path: Optional[str] = Field(None, description="Vocabulary file path")
