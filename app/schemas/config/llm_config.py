from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    confloat,
    conint,
    constr,
    field_validator,
)


class LLMConfig(BaseModel):
    """Configuration for LLM settings."""

    model_name: constr(min_length=1) = Field(..., description="Name of the LLM model")
    api_key: SecretStr = Field(..., description="API key for accessing the LLM service")
    temperature: confloat(ge=0, le=1) = Field(
        default=0.7, ge=0, le=1, description="Sampling temperature for the LLM"
    )
    max_tokens: conint(gt=0) = Field(
        default=1000, gt=0, description="Maximum number of tokens to generate"
    )

    @field_validator("temperature", mode="before")
    def validate_temperature(self, v):
        """Ensure temperature is between 0 and 1."""
        if not (0 <= v <= 1):
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @field_validator("max_tokens", mode="before")
    def validate_max_tokens(self, v):
        """Ensure max_tokens is a positive integer."""
        if v <= 0:
            raise ValueError("Max tokens must be a positive integer")
        return v
