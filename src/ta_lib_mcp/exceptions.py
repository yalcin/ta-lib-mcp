"""Custom exception hierarchy for ta-lib-mcp."""


class TALibMCPError(Exception):
    """Base exception for all ta-lib-mcp errors."""


class TALibUnavailableError(TALibMCPError):
    """Raised when TA-Lib is not available in the environment."""


class ValidationError(TALibMCPError):
    """Raised when input validation fails."""


class ComputationError(TALibMCPError):
    """Raised when an indicator computation fails."""
