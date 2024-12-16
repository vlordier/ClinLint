# app/routers/health.py

from fastapi import APIRouter

from app.schemas.search_schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Check API health status."""
    return HealthResponse(status="healthy", version="1.0.0")
