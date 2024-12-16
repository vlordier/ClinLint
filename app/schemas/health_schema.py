""" Health check response schema. """

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
