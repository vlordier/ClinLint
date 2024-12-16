from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class RuleValidationModel(BaseModel):
    """Model for validating Vale rules."""

    name: str = Field(..., description="Rule name")
    severity: Literal["suggestion", "warning", "error"] = Field(..., description="Rule severity")
    description: str = Field(..., description="Rule description")

    @field_validator("name")
    def validate_name(self, v):
        """Validate the rule name."""
        if not v:
            raise ValueError("Rule name must be provided")
        return v

class ConfigValidationModel(BaseModel):
    """Model for validating Vale configurations."""

    styles_path: str = Field(..., description="Path to the Vale styles directory")
    min_alert_level: Literal["suggestion", "warning", "error"] = Field(
        default="suggestion", description="Minimum alert level for Vale"
    )
    config_name: Optional[str] = Field(None, description="Configuration name")

    @field_validator("styles_path")
    def validate_styles_path(self, v):
        """Validate the styles path."""
        if not v:
            raise ValueError("Styles path must be provided")
        return v

class VocabularyValidationModel(BaseModel):
    """Model for validating Vale vocabularies."""

    name: str = Field(..., description="Vocabulary name")
    category: str = Field(..., description="Vocabulary category")
    type: Literal["accept", "reject"] = Field(..., description="Vocabulary type")
    description: Optional[str] = Field(None, description="Vocabulary description")

    @field_validator("name")
    def validate_name(self, v):
        """Validate the vocabulary name."""
        if not v:
            raise ValueError("Vocabulary name must be provided")
        return v

class PackageValidationModel(BaseModel):
    """Model for validating Vale packages."""

    package_name: str = Field(..., description="Package name")
    version: str = Field(..., description="Package version")
    description: Optional[str] = Field(None, description="Package description")

    @field_validator("package_name")
    def validate_package_name(self, v):
        """Validate the package name."""
        if not v:
            raise ValueError("Package name must be provided")
        return v

class StyleValidationModel(BaseModel):
    """Model for validating Vale styles."""

    style_name: str = Field(..., description="Style name")
    description: Optional[str] = Field(None, description="Style description")
    version: Optional[str] = Field(None, description="Style version")

    @field_validator("style_name")
    def validate_style_name(self, v):
        """Validate the style name."""
        if not v:
            raise ValueError("Style name must be provided")
        return v
class ActionValidationModel(BaseModel):
    """Model for validating Vale actions."""

    action_name: str = Field(..., description="Action name")
    script_content: str = Field(..., description="Action script content")

    @field_validator("action_name")
    def validate_action_name(self, v):
        """Validate the action name."""
        if not v:
            raise ValueError("Action name must be provided")
        return v
