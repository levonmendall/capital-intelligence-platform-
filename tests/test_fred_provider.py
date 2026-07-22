"""Tests for the FRED data provider."""

import pytest

from providers.fred import FREDProvider, FREDProviderError


class FakeResponse:
    """Minimal HTTP response used for provider tests."""

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "observations": [
                {"date": "2026-06-01", "value": "."},
                {"date": "2026-05-01", "value": "4.2"},
            ]
        }


def test_provider_requires_api_key() -> None:
    """Provider should clearly fail without credentials."""

    provider = FREDProvider(api_key=None)

    with pytest.raises(FREDProviderError):
        provider.get_latest_value("UNRATE")


def test_provider_parses_valid_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider should ignore missing values and parse numbers."""

    monkeypatch.setattr(
        "providers.fred.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    provider = FREDProvider(api_key="test-key")
    observation = provider.get_latest_value("UNRATE")

    assert observation.date == "2026-05-01"
    assert observation.value == 4.2
