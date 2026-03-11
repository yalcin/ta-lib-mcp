"""FastMCP server entry point for ta-lib-mcp.

This MCP server is strictly read-only. It wraps the TA-Lib technical
analysis library, providing indicator discovery and computation tools.
No side effects, no exchange connections.
"""

import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

import ta_lib_mcp
from ta_lib_mcp.categories import list_categories
from ta_lib_mcp.constants import ENV_LOG_LEVEL, SERVER_DESCRIPTION, SERVER_NAME
from ta_lib_mcp.indicators import (
    compute_indicator,
    get_indicator_info,
    list_indicators,
    talib_versions,
)
from ta_lib_mcp.models import (
    CategorySummary,
    ComputationResult,
    ComputeIndicatorInput,
    GetIndicatorInfoInput,
    IndicatorInfo,
    IndicatorSummary,
    ListIndicatorsInput,
    VersionInfo,
)

logger = logging.getLogger(__name__)

# Tool annotations: all tools are read-only, non-destructive, idempotent, closed-world
_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

# Create the FastMCP server
mcp = FastMCP(SERVER_NAME, instructions=SERVER_DESCRIPTION)


# --- Tool Definitions ---


@mcp.tool(annotations=_TOOL_ANNOTATIONS)
def talib_list_indicators(
    group: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    """List TA-Lib indicators with optional group, category, and search filters.

    Returns indicator names with group and category metadata. Use the optional
    filters to narrow results by TA-Lib group, category, or keyword search.

    Args:
        group: Optional TA-Lib group filter (e.g., "Overlap Studies").
        category: Optional category filter (e.g., "Trend", "Momentum").
        search: Optional keyword search for indicator names.
        limit: Maximum number of indicators to return (1-1000).

    Returns:
        List of indicator summaries with name, group, and category.
    """
    input_model = ListIndicatorsInput(
        group=group,
        category=category,
        search=search,
        limit=limit,
    )
    raw = list_indicators(
        group=input_model.group,
        category=input_model.category,
        search=input_model.search,
        limit=input_model.limit,
    )
    return [IndicatorSummary(**row).model_dump() for row in raw]


@mcp.tool(annotations=_TOOL_ANNOTATIONS)
def talib_get_indicator_info(indicator: str) -> dict[str, Any]:
    """Get metadata for a specific TA-Lib indicator.

    Returns the indicator's group, category, display name, required inputs,
    outputs, default parameters, and lookback period.

    Args:
        indicator: TA-Lib indicator name (e.g., "SMA", "RSI", "MACD").

    Returns:
        Indicator metadata with inputs, outputs, parameters, and lookback.
    """
    input_model = GetIndicatorInfoInput(indicator=indicator)
    raw = get_indicator_info(input_model.indicator)
    return IndicatorInfo(**raw).model_dump()


@mcp.tool(annotations=_TOOL_ANNOTATIONS)
def talib_compute_indicator(
    indicator: str,
    inputs: dict[str, list[float]],
    parameters: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Compute a TA-Lib indicator from aligned numeric inputs.

    Computes the requested indicator over the provided numeric arrays and
    returns the result. All input arrays must have the same length.

    Args:
        indicator: TA-Lib indicator name (e.g., "SMA", "RSI", "MACD").
        inputs: Aligned numeric input arrays (e.g., {"close": [1.0, 2.0, 3.0]}).
        parameters: Optional indicator parameters (e.g., {"timeperiod": 14}).

    Returns:
        Computation result with indicator name, length, parameters, and output values.
    """
    input_model = ComputeIndicatorInput(
        indicator=indicator,
        inputs=inputs,
        parameters=parameters,
    )
    raw = compute_indicator(
        indicator=input_model.indicator,
        inputs=input_model.inputs,
        parameters=input_model.parameters,
    )
    return ComputationResult(**raw).model_dump()


@mcp.tool(annotations=_TOOL_ANNOTATIONS)
def talib_list_categories() -> list[dict[str, Any]]:
    """List available indicator categories with descriptions.

    Returns all indicator categories (Trend, Momentum, Volume, etc.) with
    descriptions and example indicators for each category.

    Returns:
        List of category summaries with name, description, and examples.
    """
    raw = list_categories()
    return [CategorySummary(**cat).model_dump() for cat in raw]


@mcp.tool(annotations=_TOOL_ANNOTATIONS)
def talib_get_version_info() -> dict[str, Any]:
    """Return server, Python, and TA-Lib version information.

    Returns version information including the ta-lib-mcp server version,
    TA-Lib availability, and Python version.

    Returns:
        Version information dictionary.
    """
    versions = talib_versions()
    return VersionInfo(
        mcp_server_version=ta_lib_mcp.__version__,
        python_version=sys.version,
        talib_available=versions["python_package_version"] is not None,
        talib_python_version=versions["python_package_version"],
        talib_core_version=versions["core_version"],
    ).model_dump()


def _configure_logging() -> None:
    """Configure logging to stderr with JSON-like structured output."""
    log_level = os.environ.get(ENV_LOG_LEVEL, "WARNING").upper()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    )
    root_logger = logging.getLogger("ta_lib_mcp")
    root_logger.setLevel(getattr(logging, log_level, logging.WARNING))
    root_logger.addHandler(handler)


def main() -> None:
    """Run the ta-lib-mcp server.

    Configures logging and starts the MCP server with stdio transport.
    """
    _configure_logging()

    versions = talib_versions()
    if versions["python_package_version"]:
        logger.info(
            "Starting %s v%s (TA-Lib %s)",
            SERVER_NAME,
            ta_lib_mcp.__version__,
            versions["python_package_version"],
        )
    else:
        logger.warning(
            "Starting %s v%s (TA-Lib not available). "
            "Install with `pip install TA-Lib` to enable indicator tools.",
            SERVER_NAME,
            ta_lib_mcp.__version__,
        )

    mcp.run()


if __name__ == "__main__":
    main()
