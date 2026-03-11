"""TA-Lib adapter and computation helpers."""

from __future__ import annotations

import importlib
import math
from collections.abc import Mapping, Sequence
from typing import Any

from ta_lib_mcp.categories import categorize_group
from ta_lib_mcp.constants import DEFAULT_LIMIT
from ta_lib_mcp.exceptions import ComputationError, TALibUnavailableError, ValidationError
from ta_lib_mcp.validators import (
    normalize_indicator_name,
    normalize_text_filter,
    validate_inputs,
    validate_limit,
    validate_parameters,
)


def _load_talib() -> tuple[Any, Any] | None:
    """Load TA-Lib and the abstract API if available."""
    try:
        talib = importlib.import_module("talib")
    except ModuleNotFoundError:
        return None

    try:
        abstract = importlib.import_module("talib.abstract")
    except ModuleNotFoundError:
        try:
            abstract = talib.abstract
        except AttributeError:
            abstract = None

    if abstract is None:
        return None
    return talib, abstract


def talib_versions() -> dict[str, str | None]:
    """Return installed TA-Lib package/core versions, if available."""
    loaded = _load_talib()
    if loaded is None:
        return {"python_package_version": None, "core_version": None}
    talib, _ = loaded
    try:
        package_version: str | None = str(talib.__version__)
    except AttributeError:
        package_version = None

    try:
        core_version: str | None = str(talib.__ta_version__)
    except AttributeError:
        core_version = None

    return {
        "python_package_version": package_version,
        "core_version": core_version,
    }


def _require_talib() -> tuple[Any, Any]:
    loaded = _load_talib()
    if loaded is None:
        raise TALibUnavailableError(
            "TA-Lib is not installed. Install with `pip install TA-Lib` "
            "and ensure the native TA-Lib library is available."
        )
    return loaded


def _flatten_names(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        names: list[str] = []
        for nested in value.values():
            names.extend(_flatten_names(nested))
        return names
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value]
    return [str(value)]


_metadata_cache: dict[str, Any] | None = None


def _get_metadata(talib: Any) -> tuple[dict[str, str], list[str]]:
    global _metadata_cache
    if _metadata_cache is not None:
        return _metadata_cache["group_map"], _metadata_cache["names"]
    groups = talib.get_function_groups()
    group_map: dict[str, str] = {}
    for group_name, names in groups.items():
        for name in names:
            group_map[str(name).upper()] = str(group_name)
    sorted_names = sorted({str(name).upper() for name in talib.get_functions()})
    _metadata_cache = {"group_map": group_map, "names": sorted_names}
    return group_map, sorted_names


def list_indicators(
    group: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, str]]:
    """List available TA-Lib indicators with group and category metadata.

    Args:
        group: Optional TA-Lib group filter.
        category: Optional category filter.
        search: Optional keyword search for indicator names.
        limit: Maximum number of results.

    Returns:
        List of indicator dicts with name, group, and category.

    Raises:
        TALibUnavailableError: If TA-Lib is not installed.
        ValidationError: If filter parameters are invalid.
    """
    limit = validate_limit(limit)
    talib, _ = _require_talib()

    group_filter = normalize_text_filter(group, "group")
    category_filter = normalize_text_filter(category, "category")
    search_filter = normalize_text_filter(search, "search")

    group_map, names = _get_metadata(talib)
    rows: list[dict[str, str]] = []
    for name in names:
        grp = group_map.get(name, "Unknown")
        cat = categorize_group(grp)
        if group_filter and group_filter not in grp.casefold():
            continue
        if category_filter and category_filter not in cat.casefold():
            continue
        if search_filter and search_filter not in name.casefold():
            continue
        rows.append({"name": name, "group": grp, "category": cat})
        if len(rows) >= limit:
            break

    return rows


def get_indicator_info(indicator: str) -> dict[str, Any]:
    """Return metadata about one TA-Lib indicator.

    Args:
        indicator: Indicator name (case-insensitive).

    Returns:
        Dict with indicator metadata including group, category, inputs, outputs.

    Raises:
        TALibUnavailableError: If TA-Lib is not installed.
        ValidationError: If the indicator name is invalid or unknown.
    """
    name = normalize_indicator_name(indicator)
    _, abstract = _require_talib()

    try:
        function = abstract.Function(name)
    except Exception as exc:  # pragma: no cover - backend-specific failures
        raise ValidationError(f"Unknown or unsupported indicator: {name}") from exc

    try:
        info_value = function.info
    except AttributeError:
        info_value = {}
    except Exception as exc:  # pragma: no cover - backend-specific failures
        raise ComputationError(f"Failed to read indicator metadata for `{name}`.") from exc

    raw_info = dict(info_value) if isinstance(info_value, Mapping) else {}
    input_names = _flatten_names(raw_info.get("input_names"))
    output_names = _flatten_names(raw_info.get("output_names"))
    raw_parameters = raw_info.get("parameters", {})
    parameters = dict(raw_parameters) if isinstance(raw_parameters, Mapping) else {}

    try:
        lookback_value = function.lookback
    except AttributeError:
        lookback = None
    else:
        try:
            lookback = int(lookback_value)
        except (TypeError, ValueError):
            lookback = None

    group = str(raw_info.get("group", "Unknown"))
    return {
        "indicator": name,
        "group": group,
        "category": categorize_group(group),
        "display_name": str(raw_info.get("display_name", name)),
        "inputs": [str(item) for item in input_names],
        "outputs": [str(item) for item in output_names],
        "parameters": {str(key): value for key, value in parameters.items()},
        "lookback": lookback,
    }


def _serialize_sequence(value: Any) -> list[float | None]:
    try:
        value = value.tolist()
    except AttributeError:
        pass
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ComputationError("TA-Lib returned an unexpected output type.")

    serialized: list[float | None] = []
    for item in value:
        if item is None:
            serialized.append(None)
            continue
        try:
            number = float(item)
        except (TypeError, ValueError) as exc:
            raise ComputationError("TA-Lib returned non-numeric values in the output.") from exc

        serialized.append(number if math.isfinite(number) else None)
    return serialized


def _is_nested_sequence(value: Any) -> bool:
    """Return True when value looks like a sequence of output series."""
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        return False
    try:
        first = value[0]
    except (IndexError, KeyError):
        return False
    try:
        _serialize_sequence(first)
    except ComputationError:
        return False
    return True


def compute_indicator(
    indicator: str,
    inputs: Mapping[str, Sequence[float | int]],
    parameters: Mapping[str, float | int] | None = None,
) -> dict[str, Any]:
    """Compute a TA-Lib indicator over aligned numeric arrays.

    Args:
        indicator: Indicator name (case-insensitive).
        inputs: Aligned numeric input arrays keyed by name.
        parameters: Optional indicator parameter overrides.

    Returns:
        Dict with indicator name, length, parameters, and computed result.

    Raises:
        TALibUnavailableError: If TA-Lib or NumPy is not installed.
        ValidationError: If inputs or parameters are invalid.
        ComputationError: If the indicator computation fails.
    """
    name = normalize_indicator_name(indicator)
    normalized_inputs, length = validate_inputs(inputs)
    validated_parameters = validate_parameters(parameters)
    _, abstract = _require_talib()

    try:
        np = importlib.import_module("numpy")
    except ModuleNotFoundError as exc:  # pragma: no cover - numpy is required by talib
        raise TALibUnavailableError("NumPy is required to run TA-Lib tools.") from exc

    prepared_inputs = {
        key: np.asarray(values, dtype=float) for key, values in normalized_inputs.items()
    }

    try:
        function = abstract.Function(name)
        if validated_parameters:
            function.set_parameters(validated_parameters)
        raw_output = function(prepared_inputs)
    except ValidationError:
        raise
    except Exception as exc:
        raise ComputationError(f"Failed to compute indicator `{name}`: {exc}") from exc

    try:
        info_value = function.info
    except AttributeError:
        output_names = []
    except Exception as exc:  # pragma: no cover - backend-specific failures
        raise ComputationError(f"Failed to read output metadata for `{name}`.") from exc
    else:
        raw_info = dict(info_value) if isinstance(info_value, Mapping) else {}
        output_names = [str(item) for item in _flatten_names(raw_info.get("output_names"))]

    if len(output_names) > 1:
        if not _is_nested_sequence(raw_output):
            raise ComputationError(
                "TA-Lib returned an unexpected output type for multi-output indicator."
            )

        values = [_serialize_sequence(item) for item in raw_output]
        if len(output_names) == len(values):
            result: Any = {
                str(key): value for key, value in zip(output_names, values, strict=False)
            }
        else:
            result = values
    else:
        single = _serialize_sequence(raw_output)
        if len(output_names) == 1:
            result = {str(output_names[0]): single}
        else:
            result = single

    return {
        "indicator": name,
        "length": length,
        "parameters": validated_parameters,
        "result": result,
    }
