class ConfigurationError(Exception):
    """Raised when there are configuration-related errors."""

    pass


class AnalysisError(Exception):
    """Raised when text analysis fails."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass
