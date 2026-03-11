"""Shared test fixtures for ta-lib-mcp tests."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from tests.fakes import FakeAbstract, FakeTalib

from ta_lib_mcp import indicators


@pytest.fixture
def fake_backend() -> Iterator[None]:
    """Provide a fake TA-Lib backend for testing."""
    indicators._metadata_cache = None
    with patch.object(indicators, "_load_talib", lambda: (FakeTalib(), FakeAbstract())):
        yield
    indicators._metadata_cache = None
