"""Tests for ta_lib_mcp.validators."""

from __future__ import annotations

import pytest

from ta_lib_mcp.exceptions import ValidationError
from ta_lib_mcp.validators import (
    normalize_indicator_name,
    normalize_text_filter,
    validate_inputs,
    validate_limit,
    validate_parameters,
)


def test_normalize_indicator_name_uppercases_and_trims() -> None:
    assert normalize_indicator_name(" sma ") == "SMA"


def test_normalize_text_filter_allows_none_and_empty() -> None:
    assert normalize_text_filter(None, "group") is None
    assert normalize_text_filter("   ", "group") is None


def test_normalize_text_filter_rejects_non_string() -> None:
    with pytest.raises(ValidationError, match="`group` must be a string"):
        normalize_text_filter(123, "group")  # type: ignore[arg-type]


def test_validate_limit_rejects_bool() -> None:
    with pytest.raises(ValidationError):
        validate_limit(True)


def test_validate_inputs_rejects_duplicate_keys_after_normalization() -> None:
    with pytest.raises(ValidationError, match="unique after trimming whitespace and lowercasing"):
        validate_inputs({"close": [1.0, 2.0], " Close ": [1.0, 2.0]})


def test_validate_inputs_rejects_non_finite_values() -> None:
    with pytest.raises(ValidationError, match="non-finite"):
        validate_inputs({"close": [1.0, float("inf")]})


def test_validate_parameters_rejects_duplicate_keys_after_trim() -> None:
    with pytest.raises(ValidationError, match="unique after trimming whitespace"):
        validate_parameters({"timeperiod": 14, " timeperiod ": 7})


# --- normalize_indicator_name edge cases ---


def test_normalize_indicator_name_rejects_non_string() -> None:
    with pytest.raises(ValidationError, match="non-empty string"):
        normalize_indicator_name(123)  # type: ignore[arg-type]


def test_normalize_indicator_name_rejects_empty() -> None:
    with pytest.raises(ValidationError, match="non-empty string"):
        normalize_indicator_name("   ")


# --- validate_inputs edge cases ---


def test_validate_inputs_rejects_empty_array() -> None:
    with pytest.raises(ValidationError, match="must not be empty"):
        validate_inputs({"close": []})


def test_validate_inputs_rejects_non_mapping() -> None:
    with pytest.raises(ValidationError, match="non-empty mapping"):
        validate_inputs("not a mapping")  # type: ignore[arg-type]


def test_validate_inputs_rejects_empty_mapping() -> None:
    with pytest.raises(ValidationError, match="non-empty mapping"):
        validate_inputs({})


def test_validate_inputs_rejects_non_string_keys() -> None:
    with pytest.raises(ValidationError, match="non-empty strings"):
        validate_inputs({123: [1.0, 2.0]})  # type: ignore[dict-item]


def test_validate_inputs_rejects_empty_string_keys() -> None:
    with pytest.raises(ValidationError, match="non-empty strings"):
        validate_inputs({"  ": [1.0, 2.0]})


def test_validate_inputs_rejects_non_sequence_values() -> None:
    with pytest.raises(ValidationError, match="sequence of numbers"):
        validate_inputs({"close": 42})  # type: ignore[dict-item]


def test_validate_inputs_rejects_boolean_values() -> None:
    with pytest.raises(ValidationError, match="non-numeric"):
        validate_inputs({"close": [True, False]})


# --- validate_parameters edge cases ---


def test_validate_parameters_rejects_non_mapping() -> None:
    with pytest.raises(ValidationError, match="must be a mapping"):
        validate_parameters("not a mapping")  # type: ignore[arg-type]


def test_validate_parameters_rejects_boolean_values() -> None:
    with pytest.raises(ValidationError, match="must be numeric"):
        validate_parameters({"flag": True})  # type: ignore[dict-item]


def test_validate_parameters_rejects_non_string_keys() -> None:
    with pytest.raises(ValidationError, match="non-empty strings"):
        validate_parameters({123: 42})  # type: ignore[dict-item]


# --- validate_limit edge cases ---


def test_validate_limit_rejects_zero() -> None:
    with pytest.raises(ValidationError, match="between 1 and"):
        validate_limit(0)


def test_validate_limit_rejects_negative() -> None:
    with pytest.raises(ValidationError, match="between 1 and"):
        validate_limit(-1)


def test_validate_limit_rejects_over_max() -> None:
    with pytest.raises(ValidationError, match="between 1 and"):
        validate_limit(1001)
