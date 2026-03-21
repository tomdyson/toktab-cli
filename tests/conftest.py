"""Pytest configuration and fixtures."""

import pytest


# pytest-httpx provides the httpx_mock fixture automatically


@pytest.fixture(autouse=True)
def default_text_output(monkeypatch):
    """Default to text output in tests so TTY auto-detection doesn't interfere.

    Tests that need JSON auto-detection should clear this with:
        monkeypatch.delenv("OUTPUT_FORMAT")
    """
    monkeypatch.setenv("OUTPUT_FORMAT", "text")
