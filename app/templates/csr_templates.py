from enum import Enum
from typing import Any


class CSRType(str, Enum):
    """Types of Clinical Study Reports."""

    FULL = "full"
    ABBREVIATED = "abbreviated"
    INTERIM = "interim"
    FINAL = "final"
    SUPPLEMENTARY = "supplementary"


class CSRTemplate:
    """Template for Clinical Study Reports."""

    def __init__(
        self, csr_type: CSRType, sections: list[str], required_fields: dict[str, Any]
    ):
        self.csr_type = csr_type
        self.sections = sections
        self.required_fields = required_fields


# Define templates for each CSR type
CSR_TEMPLATES = {
    CSRType.FULL: CSRTemplate(
        csr_type=CSRType.FULL,
        sections=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
        ],
        required_fields={
            "metadata": [
                "protocol_id",
                "study_title",
                "sponsor",
                "phase",
                "therapeutic_area",
                "indication",
                "study_design",
                "start_date",
                "completion_date",
                "report_date",
                "version",
            ],
            "status": ["Draft", "In Review", "Complete", "Approved", "Archived"],
            "keywords": [],
            "related_documents": [],
        },
    ),
    CSRType.ABBREVIATED: CSRTemplate(
        csr_type=CSRType.ABBREVIATED,
        sections=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        required_fields={
            "metadata": [
                "protocol_id",
                "study_title",
                "sponsor",
                "phase",
                "therapeutic_area",
                "indication",
                "study_design",
                "start_date",
                "report_date",
                "version",
            ],
            "status": ["Draft", "In Review", "Complete", "Approved", "Archived"],
            "keywords": [],
            "related_documents": [],
        },
    ),
    # Add other CSR types as needed
}
