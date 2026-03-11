"""Fake TA-Lib backend for testing."""

from __future__ import annotations

from typing import Any


class FakeFunction:
    """Simple fake for talib.abstract.Function."""

    def __init__(self, name: str) -> None:
        """Initialize fake indicator function with default parameters."""
        normalized = name.upper()
        if normalized not in {"SMA", "MACD", "RSI"}:
            raise ValueError("Unknown indicator")
        self.name = normalized
        self._params: dict[str, int | float] = {
            "timeperiod": 30,
            "fastperiod": 12,
            "slowperiod": 26,
            "signalperiod": 9,
        }

    @property
    def info(self) -> dict[str, Any]:
        if self.name == "SMA":
            return {
                "group": "Overlap Studies",
                "display_name": "Simple Moving Average",
                "input_names": {"price": "close"},
                "output_names": ["real"],
                "parameters": {"timeperiod": self._params["timeperiod"]},
            }
        if self.name == "RSI":
            return {
                "group": "Momentum Indicators",
                "display_name": "Relative Strength Index",
                "input_names": {"price": "close"},
                "output_names": ["real"],
                "parameters": {"timeperiod": self._params["timeperiod"]},
            }
        return {
            "group": "Momentum Indicators",
            "display_name": "MACD",
            "input_names": {"price": "close"},
            "output_names": ["macd", "macdsignal", "macdhist"],
            "parameters": {
                "fastperiod": self._params["fastperiod"],
                "slowperiod": self._params["slowperiod"],
                "signalperiod": self._params["signalperiod"],
            },
        }

    @property
    def lookback(self) -> int:
        if self.name == "SMA":
            return 29
        if self.name == "RSI":
            return 13
        return 33

    def set_parameters(self, params: dict[str, int | float]) -> None:
        self._params.update(params)

    def __call__(self, inputs: dict[str, Any]) -> Any:
        close = inputs["close"]
        if self.name in ("SMA", "RSI"):
            return close + 1.0
        return [close + 1.0, close + 2.0, close + 3.0]


class FakeTalib:
    """Minimal talib module fake."""

    __version__ = "0.4.99"
    __ta_version__ = "0.6.99"

    @staticmethod
    def get_functions() -> list[str]:
        return ["SMA", "EMA", "MACD", "RSI"]

    @staticmethod
    def get_function_groups() -> dict[str, list[str]]:
        return {
            "Overlap Studies": ["SMA", "EMA"],
            "Momentum Indicators": ["MACD", "RSI"],
        }


class FakeAbstract:
    """Minimal talib.abstract fake."""

    Function = FakeFunction
