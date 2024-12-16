from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.schemas.csr_schemas import (
    CSR,
    CSRMetadata,
    CSRSearchParams,
    CSRType,
    Section,
    StudyDesign,
    StudyPhase,
    TherapeuticArea,
)
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_csr():
    """Create a sample CSR for testing."""
    return CSR(
        metadata=CSRMetadata(
            protocol_id="PROTO-123",
            study_title="Sample Study",
            sponsor="Test Pharma",
            phase=StudyPhase.PHASE_2,
            therapeutic_area=TherapeuticArea.ONCOLOGY,
            indication="Cancer",
            study_design=StudyDesign.RANDOMIZED,
            start_date=date(2023, 1, 1),
            completion_date=date(2023, 12, 31),
            report_date=date(2024, 1, 15),
            version="1.0"
        ),
        type=CSRType.FINAL,
        sections=[
            Section(
                number="1.0",
                title="Introduction",
                content="Sample content",
                subsections=[]
            )
        ],
        status="Complete",
        keywords=["oncology", "phase 2"],
        related_documents=[]
    )

def test_search_csr_basic():
    """Test basic CSR search functionality."""
    params = CSRSearchParams(
        phase=StudyPhase.PHASE_2.value,
        therapeutic_area=TherapeuticArea.ONCOLOGY.value
    )
    response = client.get("/search/csr", params=params.dict(exclude_none=True))
    response.raise_for_status()

def test_search_csr_with_date_range():
    """Test CSR search with date range."""
    params = CSRSearchParams(
        date_range=(date(2023, 1, 1), date(2024, 1, 1))
    )
    response = client.get("/search/csr", params=params.model_dump(exclude_none=True))
    response.raise_for_status()

def test_search_csr_by_section():
    """Test CSR search by specific section."""
    params = CSRSearchParams(
        section_number="1.0",
        keywords=["safety"]
    )
    response = client.get("/search/csr", params=params.model_dump(exclude_none=True))
    response.raise_for_status()

def test_search_csr_invalid_params():
    """Test CSR search with invalid parameters."""
    # Test with invalid phase parameter directly in request
    response = client.get("/search/csr?phase=invalid_phase")
    if response.status_code != 422:
        pytest.fail(f"Expected status code 422, got {response.status_code}")
    if "input should be" not in response.json()["detail"][0]["msg"].lower():
        pytest.fail("Expected error message not found in response")

    # Test with invalid therapeutic area
    response = client.get("/search/csr?therapeutic_area=invalid_area")
    if response.status_code != 422:
        pytest.fail(f"Expected status code 422, got {response.status_code}")
    if "input should be" not in response.json()["detail"][0]["msg"].lower():
        pytest.fail("Expected error message not found in response")
