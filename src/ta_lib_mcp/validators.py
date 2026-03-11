"""Input validation and sanitization for MCP tool parameters.

All LLM-generated inputs must pass through these validators before use.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from ta_lib_mcp.constants import MAX_LIMIT
from ta_lib_mcp.exceptions import ValidationError


def normalize_indicator_name(indicator: str) -> str:
    """Validate and normalize an indicator name to uppercase.

    Args:
        indicator: Raw indicator name string.

    Returns:
        Uppercased, trimmed indicator name.

    Raises:
        ValidationError: If the indicator is not a non-empty string.
    """
    if not isinstance(indicator, str) or not indicator.strip():
        raise ValidationError("`indicator` must be a non-empty string.")
    return indicator.strip().upper()


def normalize_text_filter(value: str | None, field_name: str) -> str | None:
    """Validate optional text filters and return casefolded value.

    Args:
        value: Optional filter string.
        field_name: Name of the field for error messages.

    Returns:
        Casefolded filter string, or None if empty.

    Raises:
        ValidationError: If the value is not a string.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"`{field_name}` must be a string.")

    normalized = value.strip()
    if not normalized:
        return None
    return normalized.casefold()


def validate_limit(limit: int) -> int:
    """Validate pagination limit.

    Args:
        limit: Requested limit value.

    Returns:
        Validated limit integer.

    Raises:
        ValidationError: If limit is not an integer or out of range.
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValidationError("`limit` must be an integer.")
    if limit < 1 or limit > MAX_LIMIT:
        raise ValidationError(f"`limit` must be between 1 and {MAX_LIMIT}.")
    return limit


def validate_inputs(
    inputs: Mapping[str, Sequence[float | int]],
) -> tuple[dict[str, list[float]], int]:
    """Validate and normalize aligned numeric input arrays.

    Args:
        inputs: Mapping of input names to numeric sequences.

    Returns:
        Tuple of (normalized inputs dict, array length).

    Raises:
        ValidationError: If inputs are invalid, empty, or misaligned.
    """
    if not isinstance(inputs, Mapping) or not inputs:
        raise ValidationError("`inputs` must be a non-empty mapping.")

    normalized: dict[str, list[float]] = {}
    expected_length: int | None = None

    for key, raw_values in inputs.items():
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("Input names must be non-empty strings.")
        if isinstance(raw_values, (str, bytes, bytearray)) or not isinstance(raw_values, Sequence):
            raise ValidationError(f"Input `{key}` must be a sequence of numbers.")

        values: list[float] = []
        for item in raw_values:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise ValidationError(f"Input `{key}` contains a non-numeric value.")
            number = float(item)
            if not math.isfinite(number):
                raise ValidationError(f"Input `{key}` contains non-finite values.")
            values.append(number)

        if not values:
            raise ValidationError(f"Input `{key}` must not be empty.")

        if expected_length is None:
            expected_length = len(values)
        elif len(values) != expected_length:
            raise ValidationError("All input arrays must have the same length.")

        normalized_key = key.strip().lower()
        if normalized_key in normalized:
            raise ValidationError(
                "Input names must be unique after trimming whitespace and lowercasing."
            )
        normalized[normalized_key] = values

    return normalized, expected_length or 0


def validate_parameters(
    parameters: Mapping[str, float | int] | None,
) -> dict[str, float | int]:
    """Validate optional indicator parameter mapping.

    Args:
        parameters: Optional mapping of parameter names to numeric values.

    Returns:
        Validated parameters dict.

    Raises:
        ValidationError: If parameters contain invalid keys or non-numeric values.
    """
    if parameters is None:
        return {}
    if not isinstance(parameters, Mapping):
        raise ValidationError("`parameters` must be a mapping of numeric values.")

    validated: dict[str, float | int] = {}
    for key, value in parameters.items():
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("Parameter names must be non-empty strings.")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(f"Parameter `{key}` must be numeric.")

        normalized_key = key.strip()
        if normalized_key in validated:
            raise ValidationError("Parameter names must be unique after trimming whitespace.")
        validated[normalized_key] = value
    return validated
