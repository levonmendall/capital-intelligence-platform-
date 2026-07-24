"""Tests for the FRED data provider."""

from datetime import datetime, timezone

import pytest

from data import (
    AvailabilityBasis,
    DataQualityState,
    ObservationProvider,
    ObservationQuery,
)
from providers.fred import FREDProvider, FREDProviderError
from providers.fred_series import FRED_SERIES


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


class PointInTimeResponse:
    """FRED response containing ALFRED real-time metadata."""

    def __init__(self) -> None:
        self.request_parameters: dict | None = None

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "observations": [
                {
                    "date": "2026-06-01",
                    "value": "4.2",
                    "realtime_start": "2026-07-15",
                    "realtime_end": "2026-07-15",
                },
                {
                    "date": "2026-08-01",
                    "value": "4.8",
                    "realtime_start": "2026-08-10",
                    "realtime_end": "2026-08-15",
                },
            ]
        }


def test_provider_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider should clearly fail without credentials."""

    # Remove any GitHub Actions secret from the environment.
    monkeypatch.delenv("FRED_API_KEY", raising=False)

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


def test_fred_implements_canonical_provider_protocol() -> None:
    provider = FREDProvider(api_key="test-key")

    assert isinstance(provider, ObservationProvider)
    assert provider.name == "FRED"


def test_fetch_maps_fred_vintage_to_canonical_observation() -> None:
    response = PointInTimeResponse()
    captured: dict = {}

    def fake_get(*args, **kwargs):
        captured.update(kwargs["params"])
        return response

    retrieved_at = datetime(
        2026,
        7,
        16,
        12,
        tzinfo=timezone.utc,
    )
    as_of = datetime(
        2026,
        7,
        15,
        23,
        59,
        59,
        999999,
        tzinfo=timezone.utc,
    )
    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: retrieved_at,
        http_get=fake_get,
    )

    observations = provider.fetch(
        ObservationQuery(
            series=FRED_SERIES["unemployment"],
            as_of=as_of,
            limit=10,
        )
    )

    assert len(observations) == 1
    observation = observations[0]
    assert observation.value == 4.2
    assert observation.provenance.provider == "FRED"
    assert (
        observation.provenance.series_identifier
        == "UNRATE"
    )
    assert (
        observation.provenance.quality_state
        is DataQualityState.LIVE
    )
    assert (
        observation.provenance.availability_basis
        is AvailabilityBasis.PROVIDER_DATE
    )
    assert observation.is_available_at(as_of)
    assert captured["observation_end"] == "2026-07-15"
    assert captured["vintage_dates"] == "2026-07-15"
    assert "realtime_end" not in captured
    assert captured["limit"] == 10


def test_fetch_uses_conservative_retrieval_proxy_without_vintage() -> None:
    retrieved_at = datetime(
        2026,
        7,
        15,
        12,
        tzinfo=timezone.utc,
    )
    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: retrieved_at,
        http_get=lambda *args, **kwargs: FakeResponse(),
    )
    query = ObservationQuery(
        series=FRED_SERIES["unemployment"],
        as_of=datetime(
            2026,
            7,
            15,
            13,
            tzinfo=timezone.utc,
        ),
    )

    observation = provider.fetch(query)[0]

    assert (
        observation.provenance.released_at
        == retrieved_at
    )
    assert (
        observation.provenance.availability_basis
        is AvailabilityBasis.RETRIEVAL_PROXY
    )


def test_provider_date_is_not_available_before_end_of_day() -> None:
    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: datetime(
            2026,
            7,
            16,
            12,
            tzinfo=timezone.utc,
        ),
        http_get=lambda *args, **kwargs: PointInTimeResponse(),
    )

    with pytest.raises(
        FREDProviderError,
        match="No point-in-time observations",
    ):
        provider.fetch(
            ObservationQuery(
                series=FRED_SERIES["unemployment"],
                as_of=datetime(
                    2026,
                    7,
                    15,
                    12,
                    tzinfo=timezone.utc,
                ),
            )
        )
