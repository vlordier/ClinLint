from typing import Literal

from pydantic import BaseModel, Field, constr, field_validator


class ValeConfig(BaseModel):
    """Configuration for Vale settings."""

    styles_path: constr(min_length=1) = Field(..., description="Path to the Vale styles directory")
    min_alert_level: Literal["suggestion", "warning", "error"] = Field(
        default="suggestion", description="Minimum alert level for Vale"
    )

    @field_validator("min_alert_level", mode="before")
    def validate_min_alert_level(self, v):
        """Ensure min_alert_level is one of the allowed values."""
        if v not in {"suggestion", "warning", "error"}:
            raise ValueError("min_alert_level must be 'suggestion', 'warning', or 'error'")
        return v

    @field_validator("styles_path", mode="before")
    def validate_styles_path(self, v):
        """Validate that the styles path is provided."""
        if not v:
            raise ValueError("Styles path must be provided")
        return v
