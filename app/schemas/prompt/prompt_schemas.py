"""Schema definitions for prompt templates."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PromptVariableType(str, Enum):
    """Types of variables allowed in prompts."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


class PromptVariable(BaseModel):
    """Definition of a prompt template variable."""

    name: str = Field(..., description="Variable name")
    type: PromptVariableType = Field(..., description="Variable type")
    description: str = Field(..., description="Variable description")
    required: bool = Field(default=True, description="Whether variable is required")
    default: Optional[str] = Field(None, description="Default value if any")

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate variable name format."""
        if not v.isidentifier():
            raise ValueError("Variable name must be a valid Python identifier")
        return v


class PromptTemplate(BaseModel):
    """Definition of a prompt template."""

    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    template: str = Field(..., description="Template content")
    variables: dict[str, PromptVariable] = Field(
        default_factory=dict, description="Template variables"
    )
    tags: list[str] = Field(default_factory=list, description="Template tags")
    version: str = Field(default="1.0.0", description="Template version")

    @field_validator("template")
    def validate_template(cls, v: str) -> str:
        """Validate template format and variables."""
        import re

        # Check for valid variable placeholders
        placeholders = re.findall(r"\{(\w+)\}", v)
        if not placeholders:
            raise ValueError("Template must contain at least one variable placeholder")
        return v

    @field_validator("version")
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        import re

        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Version must be in format X.Y.Z")
        return v


class PromptValidationResult(BaseModel):
    """Results of prompt template validation."""

    is_valid: bool = Field(..., description="Whether template is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
