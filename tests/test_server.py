"""Tests for ta_lib_mcp.server tool wrappers."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

import ta_lib_mcp.server as server
from ta_lib_mcp.exceptions import TALibUnavailableError, ValidationError


def test_list_indicators_returns_list(fake_backend: None) -> None:
    result = server.talib_list_indicators()
    assert isinstance(result, list)
    assert len(result) == 4
    assert "name" in result[0]
    assert "group" in result[0]
    assert "category" in result[0]


def test_list_indicators_with_category_filter(fake_backend: None) -> None:
    result = server.talib_list_indicators(category="Trend")
    names = [row["name"] for row in result]
    assert "SMA" in names
    assert "EMA" in names
    assert "MACD" not in names


def test_get_indicator_info_returns_metadata(fake_backend: None) -> None:
    result = server.talib_get_indicator_info(indicator="SMA")
    assert result["indicator"] == "SMA"
    assert result["group"] == "Overlap Studies"
    assert result["category"] == "Trend"
    assert "inputs" in result
    assert "outputs" in result


def test_compute_indicator_returns_result(fake_backend: None) -> None:
    result = server.talib_compute_indicator(
        indicator="SMA",
        inputs={"close": [1.0, 2.0, 3.0]},
        parameters={"timeperiod": 2},
    )
    assert result["indicator"] == "SMA"
    assert result["length"] == 3
    assert "result" in result


def test_list_indicators_propagates_unavailable() -> None:
    def _raise(*args: Any, **kwargs: Any) -> None:
        raise TALibUnavailableError("missing")

    with patch.object(server, "list_indicators", _raise):
        with pytest.raises(TALibUnavailableError):
            server.talib_list_indicators()


def test_list_indicators_propagates_validation_error() -> None:
    def _raise(*args: Any, **kwargs: Any) -> None:
        raise ValidationError("bad input")

    with patch.object(server, "list_indicators", _raise):
        with pytest.raises(ValidationError):
            server.talib_list_indicators()


def test_list_categories() -> None:
    result = server.talib_list_categories()
    assert isinstance(result, list)
    assert len(result) > 0
    names = {cat["name"] for cat in result}
    assert "Trend" in names
    assert "Momentum" in names


def test_get_version_info() -> None:
    with patch.object(
        server,
        "talib_versions",
        lambda: {"python_package_version": "0.4.99", "core_version": "0.6.99"},
    ):
        result = server.talib_get_version_info()
    assert result["talib_available"] is True
    assert result["talib_python_version"] == "0.4.99"


def test_get_version_info_talib_unavailable() -> None:
    with patch.object(
        server,
        "talib_versions",
        lambda: {"python_package_version": None, "core_version": None},
    ):
        result = server.talib_get_version_info()
    assert result["talib_available"] is False
    assert result["talib_python_version"] is None
    assert result["talib_core_version"] is None
