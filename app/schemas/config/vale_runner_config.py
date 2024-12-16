from typing import Literal

from pydantic import BaseModel, Field, conint, field_validator


class ValeRunnerConfig(BaseModel):
    """Configuration for Vale runner."""

    timeout: conint(gt=0) = Field(default=30, description="Vale process timeout in seconds")
    min_alert_level: Literal["suggestion", "warning", "error"] = Field(
        default="suggestion", description="Minimum alert level"
    )
    max_issues: conint(gt=0) = Field(default=100, description="Maximum number of issues to return")
    ignore_patterns: list[str] = Field(default_factory=list, description="Patterns to ignore")

    @field_validator("timeout", "max_issues", mode="before")
    def validate_positive_integers(self, v, field):
        """Ensure timeout and max_issues are positive integers."""
        if v <= 0:
            raise ValueError(f"{field.name} must be a positive integer")
        return v
