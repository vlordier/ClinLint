from typing import Optional

from pydantic import BaseModel, Field, conint, field_validator


class ProcessingConfig(BaseModel):
    """Configuration for text processing."""

    max_batch_size: conint(gt=0) = Field(default=100, description="Maximum batch size for processing")
    batch_timeout: conint(gt=0) = Field(default=300, description="Batch processing timeout in seconds")
    max_workers: Optional[int] = Field(None, description="Maximum number of worker threads")
    retry_attempts: conint(ge=0) = Field(default=3, description="Number of retry attempts")
    retry_delay: conint(gt=0) = Field(default=1, description="Delay between retries in seconds")
    @field_validator("max_batch_size", "batch_timeout", "retry_attempts", "retry_delay", mode="before")
    def validate_positive_integers(self, v, field):
        """Ensure these fields are positive integers."""
        if field.name != "retry_attempts" and v <= 0:
            raise ValueError(f"{field.name} must be a positive integer")
        return v
