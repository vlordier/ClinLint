"""Custom types for the services module."""

from typing import Optional

from pydantic import BaseModel


class ValeIssue(BaseModel):
    Line: int
    Message: str
    Rule: str


class LLMFeedback(BaseModel):
    feedback: list[str]


class SuggestionResult(BaseModel):
    vale_issues: Optional[dict[str, list[ValeIssue]]] = None
    formatted_issues: Optional[str] = None
    suggestions: Optional[list[str]] = None
