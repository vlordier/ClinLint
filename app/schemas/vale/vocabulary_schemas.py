"""Schema definitions for Vale vocabularies and related components."""

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VocabularyType(str, Enum):
    """Types of vocabulary entries."""

    ACCEPT = "accept"
    REJECT = "reject"


class VocabularyCategory(str, Enum):
    """Categories for vocabularies."""

    MEDICAL = "medical"
    STATISTICAL = "statistical"
    THERAPEUTIC = "therapeutic"
    SAFETY = "safety"
    EFFICACY = "efficacy"
    REGULATORY = "regulatory"
    GENERAL = "general"


class VocabularyTerm(BaseModel):
    """Model for individual vocabulary terms."""

    term: str = Field(..., description="The vocabulary term")
    category: VocabularyCategory = Field(..., description="Term category")
    type: VocabularyType = Field(..., description="Accept or reject")
    case_sensitive: bool = Field(
        default=True, description="Whether term is case-sensitive"
    )
    is_regex: bool = Field(default=False, description="Whether term is a regex pattern")
    description: Optional[str] = Field(None, description="Term description")
    alternatives: Optional[list[str]] = Field(None, description="Alternative terms")
    tags: list[str] = Field(default_factory=list, description="Term tags")

    @field_validator("term")
    def validate_term(cls, v):
        """Validate term format."""
        if not v.strip():
            raise ValueError("Term cannot be empty")
        if len(v) > 100:
            raise ValueError("Term cannot exceed 100 characters")
        return v.strip()

    @field_validator("alternatives")
    def validate_alternatives(cls, v):
        """Validate alternative terms."""
        if v:
            seen = set()
            unique_alts = []
            for alt in v:
                if alt.lower() not in seen:
                    seen.add(alt.lower())
                    unique_alts.append(alt)
            return unique_alts
        return v

    @field_validator("tags")
    def validate_tags(cls, v):
        """Validate tags format."""
        if v:
            return [tag.lower() for tag in v if tag.strip()]
        return v


class VocabularyFile(BaseModel):
    """Model for vocabulary files."""

    name: str = Field(..., description="Vocabulary file name")
    category: VocabularyCategory = Field(..., description="Vocabulary category")
    type: VocabularyType = Field(..., description="Accept or reject")
    terms: list[VocabularyTerm] = Field(
        default_factory=list, description="List of terms"
    )
    description: Optional[str] = Field(None, description="File description")
    version: str = Field(default="1.0.0", description="Vocabulary version")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    author: Optional[str] = Field(None, description="Vocabulary author")

    @field_validator("name")
    def validate_name(cls, v):
        """Validate vocabulary name format."""
        if not re.match(r"^[a-z0-9_\-]+$", v):
            raise ValueError(
                "Name can only contain lowercase letters, numbers, underscores and hyphens"
            )
        return v

    @field_validator("version")
    def validate_version(cls, v):
        """Validate version format."""
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Version must be in format X.Y.Z")
        return v


class VocabularyUpdate(BaseModel):
    """Model for vocabulary update requests."""

    terms: list[str] = Field(..., description="Terms to update")
    category: Optional[VocabularyCategory] = Field(
        None, description="Category to update"
    )
    type: Optional[VocabularyType] = Field(None, description="Type to update")
    description: Optional[str] = Field(None, description="Updated description")


class VocabularyStats(BaseModel):
    """Model for vocabulary statistics."""

    total_terms: int = Field(..., description="Total number of terms")
    terms_by_category: dict[VocabularyCategory, int] = Field(
        ..., description="Terms per category"
    )
    terms_by_type: dict[VocabularyType, int] = Field(
        ..., description="Terms by accept/reject"
    )
    regex_terms: int = Field(..., description="Number of regex terms")
    case_sensitive_terms: int = Field(..., description="Number of case-sensitive terms")


class VocabularyValidation(BaseModel):
    """Model for vocabulary validation results."""

    is_valid: bool = Field(..., description="Whether vocabulary is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    stats: Optional[VocabularyStats] = Field(None, description="Vocabulary statistics")


class VocabularyMetadata(BaseModel):
    """Metadata for a vocabulary."""

    name: str = Field(..., description="Vocabulary name")
    category: str = Field(..., description="Vocabulary category")
    type: VocabularyType = Field(..., description="Vocabulary type (accept/reject)")
    description: Optional[str] = Field(None, description="Vocabulary description")
    tags: list[str] = Field(default_factory=list, description="Vocabulary tags")
class VocabularyMetadata(BaseModel):
    """Metadata for a vocabulary."""

    name: str = Field(..., description="Vocabulary name")
    category: str = Field(..., description="Vocabulary category")
    type: VocabularyType = Field(..., description="Vocabulary type (accept/reject)")
    description: Optional[str] = Field(None, description="Vocabulary description")
    tags: list[str] = Field(default_factory=list, description="Vocabulary tags")
