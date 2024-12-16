from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    confloat,
    conint,
    constr,
    field_validator,
)


class OpenAIConfig(BaseModel):
    """OpenAI-specific configuration settings."""

    api_key: SecretStr = Field(..., description="OpenAI API key")
    model: constr(min_length=1) = Field(default="gpt-3.5-turbo", description="Model name to use")
    temperature: confloat(ge=0, le=1) = Field(
        default=0.7, ge=0, le=1, description="Sampling temperature"
    )
    max_tokens: conint(gt=0) = Field(default=500, description="Maximum tokens to generate")
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
