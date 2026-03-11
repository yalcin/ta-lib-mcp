"""Constants for ta-lib-mcp."""

from typing import Final

# Server metadata
SERVER_NAME: Final[str] = "ta-lib-mcp"
SERVER_DESCRIPTION: Final[str] = (
    "Read-only MCP server for TA-Lib indicator discovery and computation. "
    "Helps LLMs compute technical analysis indicators from numeric OHLCV data."
)

# Environment variable names
ENV_LOG_LEVEL: Final[str] = "TALIB_MCP_LOG_LEVEL"

# Validation limits
DEFAULT_LIMIT: Final[int] = 200
MAX_LIMIT: Final[int] = 1000
MAX_INPUT_LENGTH: Final[int] = 256
