"""Schema definitions for Vale rules, vocabularies, and related components."""

from enum import Enum
from typing import Optional, Union
from schemas.vale.vale_config_schema import AlertLevel

from pydantic import BaseModel, Field, field_validator


class UpdateRuleTagsRequest(BaseModel):
    tags: Optional[set[str]] = Field(None, description="Tags to update")


class VocabularyType(str, Enum):
    """Types of vocabulary entries."""

    ACCEPT = "accept"
    REJECT = "reject"


class RuleType(str, Enum):
    """Types of Vale rules."""

    EXISTENCE = "existence"
    SUBSTITUTION = "substitution"
    OCCURRENCE = "occurrence"
    REPETITION = "repetition"
    CONSISTENCY = "consistency"
    CONDITIONAL = "conditional"
    CAPITALIZATION = "capitalization"
    METRIC = "metric"
    SPELLING = "spelling"
    SEQUENCE = "sequence"
    SCRIPT = "script"


class RuleSeverity(str, Enum):
    """Severity levels for Vale rules."""

    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class FileType(str, Enum):
    """Vale file type classifications."""

    MARKUP = "markup"
    CODE = "code"
    TEXT = "text"


class RuleScope(str, Enum):
    """Scopes for Vale rules."""

    HEADING = "heading"
    HEADING_H1 = "heading.h1"
    HEADING_H2 = "heading.h2"
    HEADING_H3 = "heading.h3"
    HEADING_H4 = "heading.h4"
    HEADING_H5 = "heading.h5"
    HEADING_H6 = "heading.h6"
    TABLE_HEADER = "table.header"
    TABLE_CELL = "table.cell"
    TABLE_CAPTION = "table.caption"
    FIGURE_CAPTION = "figure.caption"
    LIST = "list"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    BLOCKQUOTE = "blockquote"
    ALT = "alt"
    SUMMARY = "summary"
    RAW = "raw"
    COMMENT_LINE = "comment.line"
    COMMENT_BLOCK = "comment.block"
    TEXT = "text"


class ActionType(str, Enum):
    """Types of Vale actions."""

    SUGGEST = "suggest"
    REPLACE = "replace"
    REMOVE = "remove"
    EDIT = "edit"


class Action(BaseModel):
    """Definition of a Vale action."""

    name: ActionType = Field(..., description="Type of action")
    params: Optional[list[str]] = Field(None, description="Action parameters")


class ScopeDefinition(BaseModel):
    """Definition of rule scopes."""

    include: list[RuleScope] = Field(
        default_factory=list, description="Scopes to include"
    )
    exclude: list[RuleScope] = Field(
        default_factory=list, description="Scopes to exclude"
    )

    @field_validator("include", "exclude")
    def validate_scope_combinations(cls, v):
        """Validate that scope combinations are valid."""
        for scope in v:
            if scope in [RuleScope.COMMENT_LINE, RuleScope.COMMENT_BLOCK]:
                if any(s in v for s in [RuleScope.HEADING, RuleScope.PARAGRAPH]):
                    raise ValueError("Cannot mix code and markup scopes")
        return v


class ValeRuleModel(BaseModel):
    """Model for Vale rule."""

    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    severity: RuleSeverity = Field(..., description="Rule severity level")
    scope: RuleScope = Field(..., description="Rule scope")
    pattern: Optional[str] = Field(None, description="Regex pattern for matching")
    action: Optional[Action] = Field(None, description="Action to take on match")

    @field_validator("pattern")
    def validate_pattern(cls, v):
        """Validate regex pattern."""
        if v:
            import re
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class ValeVocabularyModel(BaseModel):
    """Model for Vale vocabulary."""

    name: str = Field(..., description="Vocabulary name")
    terms: list[str] = Field(default_factory=list, description="List of terms")
    type: VocabularyType = Field(..., description="Vocabulary type (accept/reject)")

    @field_validator("terms")
    def validate_terms(cls, v):
        """Validate terms list."""
        if not v:
            raise ValueError("Terms list cannot be empty")
        return v


class ValePackageModel(BaseModel):
    """Model for Vale package."""

    name: str = Field(..., description="Package name")
    description: Optional[str] = Field(None, description="Package description")
    rules: list[ValeRuleModel] = Field(default_factory=list, description="List of rules")
    vocabularies: list[ValeVocabularyModel] = Field(default_factory=list, description="List of vocabularies")


class ValeConfigModel(BaseModel):
    """Model for Vale configuration."""

    styles_path: str = Field(..., description="Path to styles directory")
    min_alert_level: AlertLevel = Field(default=AlertLevel.WARNING, description="Minimum alert level")
    packages: list[ValePackageModel] = Field(default_factory=list, description="List of packages")


class ValeStyleModel(BaseModel):
    """Model for Vale style."""

    name: str = Field(..., description="Style name")
    extends: Optional[str] = Field(None, description="Parent style")
    rules: list[ValeRuleModel] = Field(default_factory=list, description="List of rules in style")
    vocabularies: list[ValeVocabularyModel] = Field(default_factory=list, description="List of vocabularies in style")

    """Definition of a Vale rule."""

    extends: RuleType = Field(..., description="Base rule type")
    message: str = Field(..., description="Error message to display")
    level: RuleSeverity = Field(..., description="Rule severity level")
    scope: Union[RuleScope, list[RuleScope], ScopeDefinition] = Field(
        ..., description="Rule application scope(s)"
    )
    pattern: Optional[str] = Field(None, description="Regex pattern for matching")
    tokens: Optional[list[str]] = Field(None, description="Token list for matching")
    exceptions: Optional[list[str]] = Field(None, description="Patterns to ignore")
    link: Optional[str] = Field(None, description="Reference link")
    action: Optional[Action] = Field(None, description="Correction action")


class ValePackage(BaseModel):
    """Model for Vale package information."""

    name: str = Field(..., description="Package name")
    description: Optional[str] = Field(None, description="Package description")
    rules: list[str] = Field(
        default_factory=list, description="Available rules in package"
    )


class ValeVocabulary(BaseModel):
    """Model for Vale vocabulary information."""

    name: str = Field(..., description="Vocabulary name")
    category: str = Field(..., description="Vocabulary category")
    terms: list[str] = Field(default_factory=list, description="Terms in vocabulary")
    type: str = Field(..., description="Vocabulary type (accept/reject)")


class ValeStats(BaseModel):
    """Model for Vale statistics."""

    total_packages: int = Field(..., description="Total number of packages")
    total_rules: int = Field(..., description="Total number of rules")
    total_vocabularies: int = Field(..., description="Total number of vocabularies")
    rules_per_package: dict[str, int] = Field(
        ..., description="Number of rules per package"
    )
    vocab_per_category: dict[str, int] = Field(
        ..., description="Number of vocabularies per category"
    )


class ValidationResult(BaseModel):
    """Model for validation results."""

    is_valid: bool = Field(..., description="Whether the configuration is valid")
    errors: list[str] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )


class RuleValidationRequest(BaseModel):
    """Model for rule validation request."""

    rule_name: str = Field(..., description="Name of the rule to validate")
    rule_content: dict = Field(..., description="Rule definition to validate")
    rules: Optional[list[str]] = Field(None, description="List of rules to apply")
    vocabularies: Optional[list[str]] = Field(
        None, description="List of vocabularies to apply"
    )
    text: Optional[str] = Field(None, description="Text to validate against rules")
    use_llm: Optional[bool] = Field(
        False, description="Whether to use LLM for feedback"
    )


class RuleMetadata(BaseModel):
    """Model for rule metadata."""

    name: str = Field(..., description="Rule name")
    version: str = Field(..., description="Rule version")
    last_updated: str = Field(..., description="Last update timestamp")
    author: Optional[str] = Field(None, description="Rule author")
    tags: set[str] = Field(default_factory=set, description="Rule tags")


class RuleHistory(BaseModel):
    """Model for rule version history."""

    version: str = Field(..., description="Version number")
    changes: list[str] = Field(..., description="List of changes")
    timestamp: str = Field(..., description="Change timestamp")
    author: Optional[str] = Field(None, description="Change author")


class PackageStats(BaseModel):
    """Model for package statistics."""

    total_rules: int = Field(..., description="Total number of rules")
    rules_by_severity: dict[str, int] = Field(
        ..., description="Rules count by severity"
    )
    rules_by_category: dict[str, int] = Field(
        ..., description="Rules count by category"
    )
    active_rules: int = Field(..., description="Number of active rules")


class RuleContent(BaseModel):
    """Pydantic model for rule content."""

    message: str
    level: str
    scope: str
    pattern: Optional[str] = None
