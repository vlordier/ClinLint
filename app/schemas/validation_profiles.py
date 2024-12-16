"""Predefined validation profiles for different CSR types."""

from .csr.csr_schema import (
    CSRRuleSet,
    CSRType,
    CSRValidationProfile,
    CSRVocabularySet,
    RuleMetadata,
    StudyPhase,
    TherapeuticArea,
    VocabularyMetadata,
)

# Example validation profile for a final CSR
FINAL_CSR_PROFILE = CSRValidationProfile(
    csr_type=CSRType.FINAL,
    rule_set=CSRRuleSet(
        csr_type=CSRType.FINAL,
        required_rules=[
            RuleMetadata(
                name="ICHCompliance",
                package="CSR",
                severity="error",
                description="Ensures compliance with ICH E3 guidelines",
                tags={"ich", "compliance", "regulatory"},
            ),
            RuleMetadata(
                name="StatisticalReporting",
                package="CSR",
                severity="error",
                description="Validates statistical result reporting",
                tags={"statistics", "results", "accuracy"},
            ),
        ],
        section_specific_rules={
            "13": [  # Safety evaluation section
                RuleMetadata(
                    name="SafetyReporting",
                    package="CSR.Safety",
                    severity="error",
                    description="Validates safety data reporting",
                    tags={"safety", "adverse-events"},
                )
            ]
        },
    ),
    vocabulary_set=CSRVocabularySet(
        csr_type=CSRType.FINAL,
        required_vocabularies=[
            VocabularyMetadata(
                name="medical_terms",
                category="medical",
                type="accept",
                description="Standard medical terminology",
                tags={"medical", "terminology"},
            )
        ],
        therapeutic_area_vocabularies={
            TherapeuticArea.ONCOLOGY: [
                VocabularyMetadata(
                    name="oncology_terms",
                    category="therapeutic_areas",
                    type="accept",
                    description="Oncology-specific terminology",
                    tags={"oncology", "cancer"},
                )
            ]
        },
        phase_specific_vocabularies={
            StudyPhase.PHASE_3: [
                VocabularyMetadata(
                    name="phase3_terms",
                    category="study_phase",
                    type="accept",
                    description="Phase 3 specific terminology",
                    tags={"phase3", "pivotal"},
                )
            ]
        },
    ),
    required_sections=[
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
    validation_level="strict",
)

# Dictionary mapping CSR types to their validation profiles
VALIDATION_PROFILES: dict[CSRType, CSRValidationProfile] = {
    CSRType.FINAL: FINAL_CSR_PROFILE,
    # Add other profiles as needed
}


def get_validation_profile(csr_type: CSRType) -> CSRValidationProfile:
    """Get the validation profile for a specific CSR type.

    Args:
        csr_type: Type of CSR

    Returns:
        Corresponding validation profile

    Raises:
        KeyError: If no profile exists for the CSR type
    """
    if csr_type not in VALIDATION_PROFILES:
        raise KeyError(f"No validation profile found for CSR type: {csr_type}")
    return VALIDATION_PROFILES[csr_type]
