from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.csr.csr_schema import CSRType, StudyDesign, StudyPhase, TherapeuticArea


class CSRSearchParams(BaseModel):
    """Parameters for searching CSRs."""

    protocol_id: Optional[str] = Field(None, description="Protocol identifier")
    study_title: Optional[str] = Field(None, description="Study title search term")
    phase: Optional[StudyPhase] = Field(None, description="Study phase")
    therapeutic_area: Optional[TherapeuticArea] = Field(
        None, description="Therapeutic area"
    )
    csr_type: Optional[CSRType] = Field(None, description="Type of CSR")
    study_design: Optional[StudyDesign] = Field(None, description="Study design type")
    date_range: Optional[tuple[str, str]] = Field(
        None, description="Date range for report_date"
    )
    section_number: Optional[str] = Field(None, description="Specific section number")
    keywords: Optional[list[str]] = Field(None, description="Keywords to search for")
    status: Optional[str] = Field(None, description="CSR status")
