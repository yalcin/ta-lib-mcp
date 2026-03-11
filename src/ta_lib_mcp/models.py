"""Pydantic models for MCP tool inputs and outputs."""

from typing import Any

from pydantic import BaseModel, Field

from ta_lib_mcp.constants import DEFAULT_LIMIT, MAX_INPUT_LENGTH, MAX_LIMIT

# --- Input Models ---


class ListIndicatorsInput(BaseModel):
    """Input for talib_list_indicators tool."""

    group: str | None = Field(
        default=None,
        description=(
            "Optional TA-Lib group filter. "
            "Examples: 'Overlap Studies', 'Momentum Indicators', 'Volume Indicators'."
        ),
        max_length=MAX_INPUT_LENGTH,
    )
    category: str | None = Field(
        default=None,
        description=(
            "Optional category filter. Examples: 'Trend', 'Momentum', 'Volume', 'Volatility'."
        ),
        max_length=MAX_INPUT_LENGTH,
    )
    search: str | None = Field(
        default=None,
        description="Optional keyword search filter for indicator names.",
        max_length=MAX_INPUT_LENGTH,
    )
    limit: int = Field(
        default=DEFAULT_LIMIT,
        description=f"Maximum number of indicators to return (1-{MAX_LIMIT}).",
        ge=1,
        le=MAX_LIMIT,
    )


class GetIndicatorInfoInput(BaseModel):
    """Input for talib_get_indicator_info tool."""

    indicator: str = Field(
        description="TA-Lib indicator name (e.g., 'SMA', 'RSI', 'MACD').",
        max_length=MAX_INPUT_LENGTH,
    )


class ComputeIndicatorInput(BaseModel):
    """Input for talib_compute_indicator tool."""

    indicator: str = Field(
        description="TA-Lib indicator name (e.g., 'SMA', 'RSI', 'MACD').",
        max_length=MAX_INPUT_LENGTH,
    )
    inputs: dict[str, list[float]] = Field(
        description=(
            "Aligned numeric input arrays keyed by name. Example: {'close': [1.0, 2.0, 3.0]}."
        ),
    )
    parameters: dict[str, float] | None = Field(
        default=None,
        description="Optional indicator parameters. Example: {'timeperiod': 14}.",
    )


# --- Output Models ---


class IndicatorSummary(BaseModel):
    """Summary of a single indicator."""

    name: str = Field(description="Indicator name (uppercase).")
    group: str = Field(description="TA-Lib function group.")
    category: str = Field(description="Indicator category.")


class IndicatorInfo(BaseModel):
    """Detailed indicator metadata."""

    indicator: str = Field(description="Indicator name.")
    group: str = Field(description="TA-Lib function group.")
    category: str = Field(description="Indicator category.")
    display_name: str = Field(description="Human-readable display name.")
    inputs: list[str] = Field(description="Required input names.")
    outputs: list[str] = Field(description="Output names.")
    parameters: dict[str, Any] = Field(description="Default parameter values.")
    lookback: int | None = Field(description="Lookback period in bars.")


class CategorySummary(BaseModel):
    """An indicator category."""

    name: str = Field(description="Category name.")
    description: str = Field(description="Category description.")
    examples: str = Field(description="Example indicators in this category.")


class ComputationResult(BaseModel):
    """Result of an indicator computation."""

    indicator: str = Field(description="Indicator name.")
    length: int = Field(description="Input array length.")
    parameters: dict[str, float | int] = Field(description="Parameters used.")
    result: Any = Field(description="Computed output values.")


class VersionInfo(BaseModel):
    """Version and environment information."""

    mcp_server_version: str = Field(description="ta-lib-mcp server version.")
    python_version: str = Field(description="Python version.")
    talib_available: bool = Field(description="Whether TA-Lib is installed.")
    talib_python_version: str | None = Field(description="TA-Lib Python package version.")
    talib_core_version: str | None = Field(description="TA-Lib C library version.")
