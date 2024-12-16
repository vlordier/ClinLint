"""Schema definitions for Vale styles."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class StyleRule(BaseModel):
    """Schema for a Vale style rule."""
    name: str = Field(..., description="Name of the rule")
    description: Optional[str] = Field(None, description="Rule description")
    level: str = Field(..., description="Rule severity level")
    scope: str = Field(..., description="Rule scope")
    pattern: str = Field(..., description="Rule pattern")
    message: str = Field(..., description="Rule message")
    link: Optional[str] = Field(None, description="Documentation link")
    
class Style(BaseModel):
    """Schema for a complete Vale style."""
    name: str = Field(..., description="Style name")
    rules: Dict[str, StyleRule] = Field(..., description="Style rules")
    extends: Optional[List[str]] = Field(default_factory=list, description="Extended styles")
    path: Optional[str] = Field(None, description="Style file path")
