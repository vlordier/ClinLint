"""Schema definitions for Vale configuration."""

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class Format(str, Enum):
    """Supported markup formats."""

    MD = "md"
    MDAST = "mdast"
    HTML = "html"
    RST = "rst"
    ASCIIDOC = "asciidoc"
    ODT = "odt"
    DOCX = "docx"
    DITA = "dita"


class AlertLevel(str, Enum):
    """Alert severity levels."""

    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class BasedOnConfig(BaseModel):
    """Configuration for BasedOn setting."""

    styles: list[str] = Field(default_factory=list, description="Style references")
    packages: list[str] = Field(default_factory=list, description="Package references")


class StyleConfig(BaseModel):
    """Configuration for a Vale style."""

    extends: Optional[str] = Field(None, description="Parent style")
    ignore: Optional[list[str]] = Field(None, description="Patterns to ignore")
    rules: dict[str, bool] = Field(default_factory=dict, description="Rule toggles")
    transforms: Optional[dict[str, str]] = Field(
        None, description="Text transformations"
    )
    tokens: Optional[dict[str, list[str]]] = Field(None, description="Custom tokens")


class VocabularyConfig(BaseModel):
    """Configuration for Vale vocabularies."""

    accept: list[str] = Field(default_factory=list, description="Accepted terms")
    reject: list[str] = Field(default_factory=list, description="Rejected terms")
    use: Optional[list[str]] = Field(None, description="Vocabulary references")


class FormatConfig(BaseModel):
    """Configuration for format-specific settings."""

    comments: Optional[bool] = Field(None, description="Check comments")
    code: Optional[bool] = Field(None, description="Check code blocks")
    headings: Optional[bool] = Field(None, description="Check headings")
    lists: Optional[bool] = Field(None, description="Check lists")
    tables: Optional[bool] = Field(None, description="Check tables")
    transform: Optional[str] = Field(None, description="XSLT transform for XML files")
    block_ignores: list[str] = Field(
        default_factory=list, description="Regex patterns for ignoring blocks"
    )
    token_ignores: list[str] = Field(
        default_factory=list, description="Regex patterns for ignoring inline tokens"
    )


class MarkupFormat(str, Enum):
    """Supported markup formats."""

    MARKDOWN = "md"
    HTML = "html"
    RST = "rst"
    ASCIIDOC = "asciidoc"
    DITA = "dita"
    XML = "xml"
    ORG = "org"


class CodeFormat(str, Enum):
    """Supported code formats."""

    C = "c"
    CS = "cs"
    CPP = "cpp"
    CSS = "css"
    GO = "go"
    HASKELL = "hs"
    JAVA = "java"
    JAVASCRIPT = "js"
    JULIA = "jl"
    LESS = "less"
    LUA = "lua"
    PERL = "pl"
    PHP = "php"
    POWERSHELL = "ps1"
    PROTOBUF = "proto"
    PYTHON = "py"
    R = "r"
    RUBY = "rb"
    RUST = "rs"
    SASS = "sass"
    SCALA = "scala"
    SWIFT = "swift"
    TYPESCRIPT = "ts"


class SyntaxConfig(BaseModel):
    """Configuration for syntax-specific settings."""

    format: Union[MarkupFormat, CodeFormat] = Field(..., description="File format")
    settings: FormatConfig = Field(..., description="Format-specific settings")


class ValeConfig(BaseModel):
    """Main Vale configuration schema."""

    StylesPath: str = Field(..., description="Path to styles directory")
    MinAlertLevel: AlertLevel = Field(
        default=AlertLevel.WARNING, description="Minimum alert level"
    )

    # Core settings
    Packages: Optional[list[str]] = Field(None, description="Package references")
    BasedOn: Optional[Union[str, BasedOnConfig]] = Field(
        None, description="Base configuration"
    )
    Vocab: Optional[VocabularyConfig] = Field(None, description="Vocabulary settings")

    # Format settings
    Formats: Optional[dict[Format, dict[str, bool]]] = Field(
        None, description="Format-specific settings"
    )

    # Syntax settings
    Syntax: Optional[dict[str, SyntaxConfig]] = Field(
        None, description="Syntax-specific settings"
    )

    # Output settings
    OutputFormat: Optional[str] = Field(None, description="Output format")

    # Project settings
    Project: Optional[str] = Field(None, description="Project name")

    # Style configurations
    StyleSettings: Optional[dict[str, StyleConfig]] = Field(
        None, description="Style-specific settings"
    )

    # Global vocabulary
    AcceptedTerms: Optional[list[str]] = Field(
        None, description="Globally accepted terms"
    )
    RejectedTerms: Optional[list[str]] = Field(
        None, description="Globally rejected terms"
    )

    # Ignore patterns
    IgnorePatterns: Optional[list[str]] = Field(
        None, description="Global ignore patterns"
    )
    SkipDirs: Optional[list[str]] = Field(None, description="Directories to skip")
    SkipFiles: Optional[list[str]] = Field(None, description="Files to skip")

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow additional fields for extensibility
