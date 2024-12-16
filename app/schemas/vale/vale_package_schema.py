"""Schema definitions for Vale packages, rules and vocabularies."""

from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class VocabularyType(str, Enum):
    """Types of vocabulary entries."""

    ACCEPT = "accept"
    REJECT = "reject"


class VocabularyEntry(BaseModel):
    """A single vocabulary entry."""

    term: str = Field(..., description="Term or regex pattern")
    case_sensitive: bool = Field(
        default=True, description="Whether term is case-sensitive"
    )
    is_regex: bool = Field(default=False, description="Whether term is a regex pattern")
    comment: Optional[str] = Field(None, description="Optional comment about the term")

    @field_validator("term")
    def validate_regex(cls, v, values):
        """Validate regex patterns if is_regex is True."""
        import re

        if values.get("is_regex", False):
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}") from e
        return v


class Vocabulary(BaseModel):
    """A complete vocabulary definition."""

    name: str = Field(..., description="Vocabulary name")
    description: Optional[str] = Field(None, description="Vocabulary description")
    accept: list[VocabularyEntry] = Field(
        default_factory=list, description="Accepted terms"
    )
    reject: list[VocabularyEntry] = Field(
        default_factory=list, description="Rejected terms"
    )
    base_path: Optional[Path] = Field(
        None, description="Base path for vocabulary files"
    )

    def save(self) -> None:
        """Save vocabulary to accept.txt and reject.txt files."""
        if not self.base_path:
            raise ValueError("base_path must be set to save vocabulary")

        vocab_dir = self.base_path / "config" / "vocabularies" / self.name
        vocab_dir.mkdir(parents=True, exist_ok=True)

        # Write accept.txt
        with open(vocab_dir / "accept.txt", "w") as f:
            for entry in self.accept:
                if entry.comment:
                    f.write(f"# {entry.comment}\n")
                if not entry.case_sensitive:
                    f.write("(?i)")
                f.write(f"{entry.term}\n")

        # Write reject.txt
        with open(vocab_dir / "reject.txt", "w") as f:
            for entry in self.reject:
                if entry.comment:
                    f.write(f"# {entry.comment}\n")
                if not entry.case_sensitive:
                    f.write("(?i)")
                f.write(f"{entry.term}\n")


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


class MarkupScope(str, Enum):
    """Scopes available for markup files."""

    HEADING = "heading"
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


class CodeScope(str, Enum):
    """Scopes available for code files."""

    COMMENT_LINE = "comment.line"
    COMMENT_BLOCK = "comment.block"


class RuleScope(str, Enum):
    """Scopes for Vale rules."""

    # Markup scopes
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

    # Code scopes
    COMMENT_LINE = "comment.line"
    COMMENT_BLOCK = "comment.block"

    # Text scope
    TEXT = "text"


class ActionType(str, Enum):
    """Types of Vale actions."""

    SUGGEST = "suggest"
    REPLACE = "replace"
    REMOVE = "remove"
    EDIT = "edit"


class EditActionType(str, Enum):
    """Types of edit actions."""

    REGEX = "regex"
    TRIM_RIGHT = "trim_right"
    TRIM_LEFT = "trim_left"
    TRIM = "trim"
    SPLIT = "split"


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


class MetricVariable(str, Enum):
    """Built-in variables for metric rules."""

    BLOCKQUOTE = "blockquote"
    CHARACTERS = "characters"
    COMPLEX_WORDS = "complex_words"
    HEADING_H1 = "heading.h1"
    HEADING_H2 = "heading.h2"
    HEADING_H3 = "heading.h3"
    HEADING_H4 = "heading.h4"
    HEADING_H5 = "heading.h5"
    HEADING_H6 = "heading.h6"
    list = "list"
    LONG_WORDS = "long_words"
    PARAGRAPHS = "paragraphs"
    POLYSYLLABIC_WORDS = "polysyllabic_words"
    PRE = "pre"
    SENTENCES = "sentences"
    SYLLABLES = "syllables"
    WORDS = "words"


class NLPToken(BaseModel):
    """Token definition for sequence rules."""

    pattern: Optional[str] = Field(None, description="Regex pattern")
    tag: Optional[str] = Field(None, description="Part-of-speech tag")
    negate: Optional[bool] = Field(None, description="Negate the match")
    skip: Optional[int] = Field(None, description="Max tokens to skip")

    @field_validator("tag")
    def validate_tag(cls, v):
        """Validate POS tags."""
        if v and not any(tag in v for tag in ["MD", "VB", "VBN", "JJ", "NN", "RB"]):
            raise ValueError(f"Invalid POS tag: {v}")
        return v


class RuleDefinition(BaseModel):
    """Definition of a Vale rule."""

    extends: RuleType = Field(..., description="Base rule type")
    message: str = Field(..., description="Error message to display")
    level: RuleSeverity = Field(..., description="Rule severity level")
    scope: Union[RuleScope, list[RuleScope], ScopeDefinition] = Field(
        ..., description="Rule application scope(s)"
    )

    # Common fields
    pattern: Optional[str] = Field(None, description="Regex pattern for matching")
    tokens: Optional[list[str]] = Field(None, description="Token list for matching")
    exceptions: Optional[list[str]] = Field(None, description="Patterns to ignore")

    # existence/substitution
    ignorecase: Optional[bool] = Field(None, description="Case-insensitive matching")
    nonword: Optional[bool] = Field(None, description="Remove word boundaries")
    append: Optional[bool] = Field(None, description="Append raw to tokens")
    raw: Optional[list[str]] = Field(None, description="Raw token patterns")
    vocab: Optional[bool] = Field(True, description="Enable vocabulary checking")

    # substitution
    swap: Optional[dict[str, str]] = Field(None, description="Term substitutions")
    capitalize: Optional[bool] = Field(None, description="Match source capitalization")

    # occurrence
    max: Optional[int] = Field(None, description="Maximum occurrences")
    min: Optional[int] = Field(None, description="Minimum occurrences")
    token: Optional[str] = Field(None, description="Token to count")

    # repetition
    alpha: Optional[bool] = Field(None, description="Match alphanumeric only")

    # consistency
    either: Optional[dict[str, str]] = Field(None, description="Term pairs")

    # conditional
    first: Optional[str] = Field(None, description="Antecedent pattern")
    second: Optional[str] = Field(None, description="Consequent pattern")

    # capitalization
    match: Optional[str] = Field(None, description="Case style to match")
    style: Optional[str] = Field(None, description="Title case style")
    indicators: Optional[list[str]] = Field(None, description="Case indicators")
    threshold: Optional[float] = Field(None, description="Match threshold")
    prefix: Optional[str] = Field(None, description="Prefix to ignore")

    # metric
    formula: Optional[str] = Field(None, description="Metric formula")
    condition: Optional[str] = Field(None, description="Metric condition")

    # spelling
    custom: Optional[bool] = Field(None, description="Disable default filters")
    filters: Optional[list[str]] = Field(None, description="Spelling filters")
    ignore: Optional[str] = Field(None, description="Words to ignore")
    dicpath: Optional[str] = Field(None, description="dictionary path")
    dictionaries: Optional[list[str]] = Field(None, description="dictionary files")

    # sequence
    nlp_tokens: Optional[list[NLPToken]] = Field(None, description="NLP token sequence")

    # script
    script: Optional[str] = Field(None, description="Tengo script content")

    # Common fields
    link: Optional[str] = Field(None, description="Reference link")
    action: Optional[Action] = Field(None, description="Correction action")

    @field_validator("scope")
    def validate_scope(cls, v):
        """Convert single scope or list to ScopeDefinition."""
        if isinstance(v, RuleScope):
            return ScopeDefinition(include=[v])
        elif isinstance(v, list):
            return ScopeDefinition(include=v)
        return v


class PackageMetadata(BaseModel):
    """Metadata for a Vale package."""

    name: str = Field(..., description="Package name")
    version: str = Field(..., description="Package version")
    description: str = Field(..., description="Package description")
    author: Optional[str] = Field(None, description="Package author")
    license: Optional[str] = Field(None, description="Package license")
    tags: set[str] = Field(default_factory=set, description="Package tags")
    dependencies: list[str] = Field(
        default_factory=list, description="Required packages"
    )


class PackageConfig(BaseModel):
    """Configuration for a Vale package."""

    metadata: PackageMetadata = Field(..., description="Package metadata")
    rules: dict[str, RuleDefinition] = Field(..., description="Rule definitions")
    vocabularies: dict[str, Vocabulary] = Field(
        default_factory=dict, description="Package vocabularies"
    )
    extends: Optional[list[str]] = Field(None, description="Parent packages")
    disabled_rules: list[str] = Field(
        default_factory=list, description="Disabled rules"
    )
    custom_settings: dict[str, str] = Field(
        default_factory=dict, description="Custom settings"
    )

    def add_vocabulary(self, vocab: Vocabulary) -> None:
        """Add a vocabulary to the package."""
        self.vocabularies[vocab.name] = vocab

    def save_vocabularies(self, base_path: Path) -> None:
        """Save all vocabularies to files."""
        for vocab in self.vocabularies.values():
            vocab.base_path = base_path
            vocab.save()


class PackageValidation(BaseModel):
    """Validation results for a Vale package."""

    is_valid: bool = Field(..., description="Overall validation status")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    rule_count: int = Field(..., description="Total number of rules")
    active_rules: int = Field(..., description="Number of active rules")
