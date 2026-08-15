import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def force_mock_provider(monkeypatch):
    """Keep the test suite deterministic regardless of the developer's .env."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
