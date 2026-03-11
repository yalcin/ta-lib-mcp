"""Tests for ta_lib_mcp.categories."""

from __future__ import annotations

from ta_lib_mcp.categories import CATEGORY_INFO, categorize_group, list_categories


def test_categorize_known_groups() -> None:
    assert categorize_group("Overlap Studies") == "Trend"
    assert categorize_group("Momentum Indicators") == "Momentum"
    assert categorize_group("Volume Indicators") == "Volume"
    assert categorize_group("Volatility Indicators") == "Volatility"
    assert categorize_group("Pattern Recognition") == "Pattern"
    assert categorize_group("Math Transform") == "Math"
    assert categorize_group("Math Operators") == "Math"


def test_categorize_unknown_group_returns_other() -> None:
    assert categorize_group("Some Future Group") == "Other"


def test_list_categories_returns_all() -> None:
    categories = list_categories()
    assert len(categories) == len(CATEGORY_INFO)
    names = {cat["name"] for cat in categories}
    assert names == set(CATEGORY_INFO.keys())
    for cat in categories:
        assert "description" in cat
        assert "examples" in cat
