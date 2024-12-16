"""Pydantic models for Clinical Study Report (CSR) and related entities."""

import re
from datetime import date
from enum import Enum
from typing import Optional

from ..vale.vale_schemas import RuleMetadata
from ..vale.vocabulary_schemas import VocabularyMetadata

from pydantic import BaseModel, Field, field_validator


class StudyPhase(str, Enum):
    """Clinical trial study phases."""

    PHASE_1 = "phase_1"
    PHASE_1A = "phase_1a"
    PHASE_1B = "phase_1b"
    PHASE_2 = "phase_2"
    PHASE_2A = "phase_2a"
    PHASE_2B = "phase_2b"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class TherapeuticArea(str, Enum):
    """Main therapeutic areas."""

    ONCOLOGY = "oncology"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    IMMUNOLOGY = "immunology"
    INFECTIOUS_DISEASES = "infectious_diseases"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    ENDOCRINOLOGY = "endocrinology"
    DERMATOLOGY = "dermatology"
    RHEUMATOLOGY = "rheumatology"
    OTHER = "other"


class CSRType(str, Enum):
    """Types of Clinical Study Reports."""

    FULL = "full"
    ABBREVIATED = "abbreviated"
    INTERIM = "interim"
    FINAL = "final"
    SUPPLEMENTARY = "supplementary"


class StudyDesign(str, Enum):
    """Clinical trial study designs."""

    RANDOMIZED = "randomized"
    NON_RANDOMIZED = "non_randomized"
    PARALLEL = "parallel"
    CROSSOVER = "crossover"
    SINGLE_ARM = "single_arm"
    OBSERVATIONAL = "observational"


class Section(BaseModel):
    """CSR section model."""

    number: str = Field(..., description="Section number (e.g., '1.1', '2.3.1')")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    subsections: list["Section"] = Field(
        default_factory=list, description="Nested subsections"
    )

    @field_validator("number")
    def validate_section_number(cls, v):
        """Validate section number format."""
        if not re.match(r"^\d+(\.\d+)*$", v):
            raise ValueError(
                "Invalid section number format. Must be like 1, 1.1, 1.1.1"
            )
        # Ensure section number depth doesn't exceed 4 levels
        if len(v.split(".")) > 4:
            raise ValueError("Section number cannot exceed 4 levels of depth")
        return v

    @field_validator("subsections")
    def validate_subsections(cls, v, info):
        """Validate subsection numbering and hierarchy."""
        values = info.data
        """Validate subsection numbering and hierarchy."""
        if not v:
            return v
        parent_num = values.get("number", "")
        for subsection in v:
            if not subsection.number.startswith(f"{parent_num}."):
                raise ValueError(
                    f"Subsection number {subsection.number} must start with parent number {parent_num}"
                )
        return v

    @field_validator("content")
    def validate_content_length(cls, v):
        """Validate content length and format."""
        if len(v) > 50000:  # Max 50K chars per section
            raise ValueError(
                "Section content exceeds maximum length of 50,000 characters"
            )
        if v.count("\n\n\n") > 0:
            raise ValueError("Content should not contain triple line breaks")
        return v

    @field_validator("title")
    def validate_title(cls, v):
        """Validate section title."""
        if not v.strip():
            raise ValueError("Section title cannot be empty")
        return v.strip()

    @field_validator("content")
    def validate_content(cls, v):
        """Validate section content."""
        if not v.strip():
            raise ValueError("Section content cannot be empty")
        return v.strip()


class CSRMetadata(BaseModel):
    """Metadata for a Clinical Study Report."""

    protocol_id: str = Field(..., description="Protocol identifier")
    study_title: str = Field(..., description="Title of the study")
    sponsor: str = Field(..., description="Study sponsor")
    phase: StudyPhase = Field(..., description="Study phase")
    therapeutic_area: TherapeuticArea = Field(..., description="Main therapeutic area")
    indication: str = Field(..., description="Specific indication")
    study_design: StudyDesign = Field(..., description="Study design type")
    start_date: date = Field(..., description="Study start date")
    completion_date: Optional[date] = Field(None, description="Study completion date")
    report_date: date = Field(..., description="CSR creation date")
    version: str = Field(..., description="CSR version number")

    @field_validator("protocol_id")
    def validate_protocol_id(cls, v):
        """Validate protocol ID format."""
        if not re.match(r"^[A-Z0-9]{2,6}-\d{3,6}$", v):
            raise ValueError(
                "Protocol ID must be in format XXX-123 with 2-6 letters/numbers followed by 3-6 digits"
            )
        return v

    @field_validator("sponsor")
    def validate_sponsor(cls, v):
        """Validate sponsor name."""
        if len(v) < 3:
            raise ValueError("Sponsor name must be at least 3 characters")
        if not re.match(r"^[A-Za-z0-9\s\-\.]+$", v):
            raise ValueError("Sponsor name contains invalid characters")
        return v

    @field_validator("version")
    def validate_version_format(cls, v):
        """Validate version number format and range."""
        major, minor, *patch = v.split(".")
        if int(major) > 99 or int(minor) > 99:
            raise ValueError("Version numbers cannot exceed 99")
        if patch and int(patch[0]) > 99:
            raise ValueError("Patch version cannot exceed 99")
        return v

    @field_validator("report_date")
    def validate_report_date_range(cls, v):
        """Validate report date is within reasonable range."""
        from datetime import date, timedelta

        min_date = date(2000, 1, 1)  # No reports before 2000
        max_date = date.today() + timedelta(days=30)  # Allow up to 30 days in future
        if v < min_date or v > max_date:
            raise ValueError(f"Report date must be between {min_date} and {max_date}")
        return v

    @field_validator("study_title")
    def validate_study_title(cls, v):
        """Validate study title."""
        if not v.strip():
            raise ValueError("Study title cannot be empty")
        return v.strip()

    @field_validator("indication")
    def validate_indication(cls, v):
        """Validate indication."""
        if not v.strip():
            raise ValueError("Indication cannot be empty")
        return v.strip()

    @field_validator("completion_date")
    def validate_completion_date(cls, v, info):
        """Validate completion date is after start date."""
        values = info.data
        """Validate completion date is after start date."""
        if v and "start_date" in values and v < values["start_date"]:
            raise ValueError("Completion date must be after start date")
        return v

    @field_validator("report_date")
    def validate_report_date(cls, v, info):
        """Validate report date is after start date."""
        values = info.data
        """Validate report date is after start date."""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("Report date must be after start date")
        return v

    @field_validator("version")
    def validate_version(cls, v):
        """Validate version format."""
        if not re.match(r"^\d+\.\d+(\.\d+)?$", v):
            raise ValueError("Version must be in format X.Y or X.Y.Z")
        return v


class CSR(BaseModel):
    """Complete Clinical Study Report model."""

    metadata: CSRMetadata = Field(..., description="CSR metadata")
    type: CSRType = Field(..., description="Type of CSR")
    sections: list[Section] = Field(..., description="CSR sections")
    status: str = Field(..., description="Current status of the CSR")
    keywords: list[str] = Field(
        default_factory=list, description="Keywords for searching"
    )
    related_documents: list[str] = Field(
        default_factory=list, description="Related document identifiers"
    )

    @field_validator("sections")
    def validate_sections(cls, v):
        """Validate sections list and ordering."""
        if not v:
            raise ValueError("CSR must have at least one section")

        # Check section numbers are in order
        section_numbers = [float(s.number.split(".")[0]) for s in v]
        if section_numbers != sorted(section_numbers):
            raise ValueError("Sections must be in numerical order")

        # Ensure required sections are present
        required_sections = {"1", "2", "3", "13", "14", "15"}  # Key ICH E3 sections
        present_sections = {s.number.split(".")[0] for s in v}
        missing = required_sections - present_sections
        if missing:
            raise ValueError(f'Missing required sections: {", ".join(missing)}')

        return v

    @field_validator("keywords")
    def validate_keywords_format(cls, v):
        """Validate keywords format and uniqueness."""
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in v:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw.lower())

        # Validate individual keywords
        for kw in unique_keywords:
            if len(kw) < 2:
                raise ValueError("Keywords must be at least 2 characters long")
            if len(kw) > 50:
                raise ValueError("Keywords cannot exceed 50 characters")
            if not re.match(r"^[a-z0-9\-\s]+$", kw):
                raise ValueError(
                    "Keywords can only contain letters, numbers, hyphens and spaces"
                )

        return unique_keywords

    @field_validator("related_documents")
    def validate_related_documents_format(cls, v):
        """Validate related document identifiers."""
        validated = []
        for doc in v:
            # Remove any whitespace
            doc = doc.strip()

            # Check format
            if not re.match(r"^[A-Z0-9\-]{5,50}$", doc):
                raise ValueError(f"Invalid document ID format: {doc}")

            # Prevent duplicates
            if doc in validated:
                continue

            validated.append(doc)

        return validated

    @field_validator("status")
    def validate_status(cls, v):
        """Validate status value."""
        valid_statuses = {"Draft", "In Review", "Complete", "Approved", "Archived"}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @field_validator("keywords")
    def validate_keywords(cls, v):
        """Validate keywords."""
        return [kw.strip().lower() for kw in v if kw.strip()]

    @field_validator("related_documents")
    def validate_related_documents(cls, v):
        """Validate related document IDs."""
        return [doc.strip() for doc in v if doc.strip()]



class CSRRuleSet(BaseModel):
    """Collection of rules associated with a CSR type."""

    csr_type: CSRType = Field(..., description="Type of CSR")
    required_rules: list[RuleMetadata] = Field(
        ..., description="Required rules for this CSR type"
    )
    recommended_rules: list[RuleMetadata] = Field(
        default_factory=list, description="Recommended but not required rules"
    )
    section_specific_rules: dict[str, list[RuleMetadata]] = Field(
        default_factory=dict, description="Rules specific to certain sections"
    )


class CSRVocabularySet(BaseModel):
    """Collection of vocabularies associated with a CSR type."""

    csr_type: CSRType = Field(..., description="Type of CSR")
    required_vocabularies: list[VocabularyMetadata] = Field(
        ..., description="Required vocabularies for this CSR type"
    )
    therapeutic_area_vocabularies: dict[TherapeuticArea, list[VocabularyMetadata]] = (
        Field(
            default_factory=dict,
            description="Vocabularies specific to therapeutic areas",
        )
    )
    phase_specific_vocabularies: dict[StudyPhase, list[VocabularyMetadata]] = Field(
        default_factory=dict, description="Vocabularies specific to study phases"
    )


class CSRValidationProfile(BaseModel):
    """Complete validation profile for a CSR type."""

    csr_type: CSRType = Field(..., description="Type of CSR")
    rule_set: CSRRuleSet = Field(..., description="Associated rule set")
    vocabulary_set: CSRVocabularySet = Field(
        ..., description="Associated vocabulary set"
    )
    required_sections: list[str] = Field(
        ..., description="Required section numbers for this CSR type"
    )
    validation_level: str = Field(
        default="standard", description="Validation strictness level"
    )


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
    date_range: Optional[tuple[date, date]] = Field(
        None, description="Date range for report_date"
    )
    section_number: Optional[str] = Field(None, description="Specific section number")
    keywords: Optional[list[str]] = Field(None, description="Keywords to search for")
    status: Optional[str] = Field(None, description="CSR status")

    @field_validator("phase", "therapeutic_area", "csr_type", "study_design", "status")
    def validate_enum_fields(cls, v, info):
        """Validate enum fields to ensure they match the expected values."""
        field_name = info.field_name
        field_type = self.model_fields[field_name].annotation
        if v is not None and v not in [
            e.value for e in field_type.__args__[0].__members__.values()
        ]:
            raise ValueError(f"Invalid value for {field_name}: {v}")
        return v
