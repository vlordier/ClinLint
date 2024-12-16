from pydantic import BaseModel, Field


class RuleSearchResult(BaseModel):
    """Model for rule search results."""
    package: str = Field(..., description="Package containing the rule")
    rule: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    severity: str = Field(..., description="Rule severity")
