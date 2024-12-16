from pydantic import BaseModel, Field

from app.schemas.vale.validation_models import ValeVocabulary

from .rule_search_result import RuleSearchResult


class SearchResults(BaseModel):
    """Model for combined search results."""
    rules: list[RuleSearchResult] = Field(default_factory=list, description="Matching rules")
    vocabularies: list[ValeVocabulary] = Field(default_factory=list, description="Matching vocabularies")
    total_matches: int = Field(..., description="Total number of matches")
    rule_matches: int = Field(..., description="Number of rule matches")
    vocabulary_matches: int = Field(..., description="Number of vocabulary matches")
