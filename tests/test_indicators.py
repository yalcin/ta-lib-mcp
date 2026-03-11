"""Tests for ta_lib_mcp.indicators."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from tests.fakes import FakeAbstract, FakeFunction

from ta_lib_mcp import indicators
from ta_lib_mcp.exceptions import ComputationError, TALibUnavailableError, ValidationError


def test_list_indicators_with_filters(fake_backend: None) -> None:
    rows = indicators.list_indicators(group="overlap", search="ma", limit=10)
    names = [row["name"] for row in rows]
    assert names == ["EMA", "SMA"]
    assert all(row["category"] == "Trend" for row in rows)


def test_list_indicators_with_category_filter(fake_backend: None) -> None:
    rows = indicators.list_indicators(category="momentum", limit=10)
    names = [row["name"] for row in rows]
    assert names == ["MACD", "RSI"]
    assert all(row["category"] == "Momentum" for row in rows)


def test_get_indicator_info(fake_backend: None) -> None:
    info = indicators.get_indicator_info("sma")
    assert info["indicator"] == "SMA"
    assert info["group"] == "Overlap Studies"
    assert info["category"] == "Trend"
    assert info["inputs"] == ["close"]
    assert info["outputs"] == ["real"]
    assert info["parameters"]["timeperiod"] == 30


def test_compute_indicator_single_output(fake_backend: None) -> None:
    result = indicators.compute_indicator(
        indicator="SMA",
        inputs={"close": [1.0, 2.0, 3.0]},
        parameters={"timeperiod": 2},
    )
    assert result["indicator"] == "SMA"
    assert result["length"] == 3
    assert result["result"]["real"] == [2.0, 3.0, 4.0]


def test_compute_indicator_multi_output(fake_backend: None) -> None:
    result = indicators.compute_indicator(
        indicator="MACD",
        inputs={"close": [1.0, 2.0, 3.0]},
    )
    assert result["indicator"] == "MACD"
    assert "macd" in result["result"]
    assert "macdsignal" in result["result"]
    assert "macdhist" in result["result"]


def test_compute_indicator_invalid_lengths(fake_backend: None) -> None:
    with pytest.raises(ValidationError):
        indicators.compute_indicator(
            indicator="SMA",
            inputs={"close": [1.0, 2.0], "open": [1.0]},
        )


def test_unavailable_talib_raises() -> None:
    with patch.object(indicators, "_load_talib", lambda: None):
        with pytest.raises(TALibUnavailableError):
            indicators.list_indicators()


def test_list_indicators_rejects_boolean_limit(fake_backend: None) -> None:
    with pytest.raises(ValidationError):
        indicators.list_indicators(limit=True)


def test_compute_indicator_rejects_duplicate_input_names(fake_backend: None) -> None:
    with pytest.raises(ValidationError):
        indicators.compute_indicator(
            indicator="SMA",
            inputs={"close": [1.0, 2.0, 3.0], " Close ": [1.0, 2.0, 3.0]},
        )


def test_compute_indicator_rejects_duplicate_parameter_names(fake_backend: None) -> None:
    with pytest.raises(ValidationError):
        indicators.compute_indicator(
            indicator="SMA",
            inputs={"close": [1.0, 2.0, 3.0]},
            parameters={"timeperiod": 2, " timeperiod ": 5},
        )


def test_compute_indicator_serializes_non_finite_values_to_none(
    fake_backend: None,
) -> None:
    def _call(self: FakeFunction, inputs: dict[str, Any]) -> Any:
        del self, inputs
        return [float("inf"), float("-inf"), float("nan")]

    with patch.object(FakeFunction, "__call__", _call):
        result = indicators.compute_indicator(
            indicator="SMA",
            inputs={"close": [1.0, 2.0, 3.0]},
        )
    assert result["result"]["real"] == [None, None, None]


def test_compute_indicator_raises_on_non_numeric_output(
    fake_backend: None,
) -> None:
    def _call(self: FakeFunction, inputs: dict[str, Any]) -> Any:
        del self, inputs
        return ["not-a-number"]

    with patch.object(FakeFunction, "__call__", _call):
        with pytest.raises(ComputationError, match="non-numeric"):
            indicators.compute_indicator(
                indicator="SMA",
                inputs={"close": [1.0, 2.0, 3.0]},
            )


def test_talib_versions_returns_none_when_module_attributes_are_missing() -> None:
    class NoVersionTalib:
        pass

    with patch.object(indicators, "_load_talib", lambda: (NoVersionTalib(), FakeAbstract())):
        versions = indicators.talib_versions()
    assert versions["python_package_version"] is None
    assert versions["core_version"] is None


def test_talib_versions_returns_none_when_talib_missing() -> None:
    with patch.object(indicators, "_load_talib", lambda: None):
        versions = indicators.talib_versions()
    assert versions["python_package_version"] is None
    assert versions["core_version"] is None


def test_compute_indicator_raises_computation_error_on_backend_failure(
    fake_backend: None,
) -> None:
    def _raise(self: FakeFunction, inputs: dict[str, Any]) -> Any:
        raise RuntimeError("boom")

    with patch.object(FakeFunction, "__call__", _raise):
        with pytest.raises(ComputationError, match="Failed to compute"):
            indicators.compute_indicator(
                indicator="SMA",
                inputs={"close": [1.0, 2.0, 3.0]},
            )


def test_compute_rsi_single_output(fake_backend: None) -> None:
    result = indicators.compute_indicator(
        indicator="RSI",
        inputs={"close": [1.0, 2.0, 3.0]},
        parameters={"timeperiod": 14},
    )
    assert result["indicator"] == "RSI"
    assert result["length"] == 3
    assert result["result"]["real"] == [2.0, 3.0, 4.0]
