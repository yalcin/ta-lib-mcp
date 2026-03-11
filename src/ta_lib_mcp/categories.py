"""Indicator classification taxonomy for TA-Lib function groups."""

from __future__ import annotations

GROUP_TO_CATEGORY: dict[str, str] = {
    "Overlap Studies": "Trend",
    "Momentum Indicators": "Momentum",
    "Volume Indicators": "Volume",
    "Volatility Indicators": "Volatility",
    "Price Transform": "Price Transform",
    "Cycle Indicators": "Cycle",
    "Pattern Recognition": "Pattern",
    "Statistic Functions": "Statistics",
    "Math Transform": "Math",
    "Math Operators": "Math",
}

CATEGORY_INFO: dict[str, dict[str, str]] = {
    "Trend": {
        "description": "Trend direction and strength indicators",
        "examples": "SMA, EMA, BBANDS, SAR, T3, DEMA, KAMA, TEMA, WMA",
    },
    "Momentum": {
        "description": "Price movement speed and magnitude oscillators",
        "examples": "RSI, MACD, STOCH, CCI, WILLR, ADX, MOM, ROC, APO",
    },
    "Volume": {
        "description": "Volume-based accumulation and flow indicators",
        "examples": "OBV, AD, ADOSC",
    },
    "Volatility": {
        "description": "Price variation and range indicators",
        "examples": "ATR, NATR, TRANGE",
    },
    "Price Transform": {
        "description": "Synthetic price derivations from OHLC data",
        "examples": "AVGPRICE, MEDPRICE, TYPPRICE, WCLPRICE",
    },
    "Cycle": {
        "description": "Hilbert Transform cycle analysis indicators",
        "examples": "HT_DCPERIOD, HT_PHASOR, HT_SINE, HT_TRENDMODE",
    },
    "Pattern": {
        "description": "Candlestick pattern recognition functions",
        "examples": "CDLDOJI, CDLHAMMER, CDLENGULFING, CDLHARAMI",
    },
    "Statistics": {
        "description": "Statistical and regression functions on price series",
        "examples": "STDDEV, VAR, LINEARREG, BETA, CORREL, TSF",
    },
    "Math": {
        "description": "Mathematical transforms and arithmetic operators",
        "examples": "SIN, COS, SQRT, LN, ADD, SUB, MULT, DIV",
    },
}


def categorize_group(group_name: str) -> str:
    """Map a TA-Lib function group to a broader category."""
    return GROUP_TO_CATEGORY.get(group_name, "Other")


def list_categories() -> list[dict[str, str]]:
    """Return all indicator categories with descriptions."""
    return [{"name": name, **info} for name, info in CATEGORY_INFO.items()]
