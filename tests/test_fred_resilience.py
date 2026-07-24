"""Tests for resilient, point-in-time-safe FRED retrieval."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import requests

from data import DataQualityState, ObservationQuery
from providers.fred import (
    FREDProvider,
    FREDProviderError,
    FREDRetrievalPolicy,
)
from providers.fred_cache import (
    FREDCacheRecord,
    JsonFREDCache,
    MemoryFREDCache,
    fred_cache_key,
)
from providers.fred_series import FRED_SERIES


class SuccessfulResponse:
    status_code = 200

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
                }
            ]
        }


class RateLimitedResponse:
    status_code = 429

    def raise_for_status(self) -> None:
        raise requests.HTTPError(
            "rate limited",
            response=self,
        )


def _query() -> ObservationQuery:
    return ObservationQuery(
        series=FRED_SERIES["unemployment"],
        as_of=datetime(
            2026,
            7,
            16,
            23,
            59,
            tzinfo=timezone.utc,
        ),
    )


def test_cache_key_excludes_api_credentials() -> None:
    first = fred_cache_key(
        "https://example.test/fred",
        {"series_id": "UNRATE", "api_key": "secret-one"},
    )
    second = fred_cache_key(
        "https://example.test/fred",
        {"api_key": "secret-two", "series_id": "UNRATE"},
    )

    assert first == second
    assert "secret" not in first


def test_memory_cache_returns_defensive_copies() -> None:
    cache = MemoryFREDCache()
    record = FREDCacheRecord(
        key="request",
        payload={"observations": [{"value": "4.2"}]},
        retrieved_at=datetime(
            2026,
            7,
            16,
            tzinfo=timezone.utc,
        ),
    )
    cache.put(record)

    loaded = cache.get("request")
    assert loaded is not None
    loaded.payload["observations"][0]["value"] = "99"

    assert (
        cache.get("request").payload["observations"][0]["value"]
        == "4.2"
    )


def test_json_cache_round_trips_offline_fixture(
    tmp_path,
) -> None:
    path = tmp_path / "fred-cache.json"
    cache = JsonFREDCache(path)
    retrieved_at = datetime(
        2026,
        7,
        16,
        12,
        tzinfo=timezone.utc,
    )
    record = FREDCacheRecord(
        key="fixture",
        payload={"observations": [{"value": "4.2"}]},
        retrieved_at=retrieved_at,
    )

    cache.put(record)
    loaded = JsonFREDCache(path).get("fixture")

    assert loaded is not None
    assert loaded.payload == record.payload
    assert loaded.retrieved_at == retrieved_at


def test_fresh_cache_avoids_duplicate_network_request() -> None:
    calls = 0
    times = iter(
        [
            datetime(2026, 7, 16, 12, tzinfo=timezone.utc),
            datetime(2026, 7, 16, 12, 5, tzinfo=timezone.utc),
        ]
    )

    def http_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return SuccessfulResponse()

    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: next(times),
        http_get=http_get,
        cache=MemoryFREDCache(),
    )

    live = provider.fetch(_query())[0]
    cached = provider.fetch(_query())[0]

    assert calls == 1
    assert live.provenance.quality_state is DataQualityState.LIVE
    assert (
        cached.provenance.quality_state
        is DataQualityState.CACHED
    )
    assert (
        cached.provenance.retrieved_at
        == live.provenance.retrieved_at
    )


def test_rate_limit_is_retried_with_exponential_backoff() -> None:
    responses = iter(
        [
            RateLimitedResponse(),
            RateLimitedResponse(),
            SuccessfulResponse(),
        ]
    )
    delays: list[float] = []
    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: datetime(
            2026,
            7,
            16,
            12,
            tzinfo=timezone.utc,
        ),
        http_get=lambda *args, **kwargs: next(responses),
        sleeper=delays.append,
        retrieval_policy=FREDRetrievalPolicy(
            max_attempts=3,
            backoff_seconds=0.5,
        ),
    )

    observation = provider.fetch(_query())[0]

    assert observation.value == 4.2
    assert delays == [0.5, 1.0]


def test_stale_cache_is_disclosed_after_provider_failure() -> None:
    times = iter(
        [
            datetime(2026, 7, 16, 12, tzinfo=timezone.utc),
            datetime(2026, 7, 16, 13, tzinfo=timezone.utc),
        ]
    )
    calls = 0

    def http_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return SuccessfulResponse()
        raise requests.Timeout("offline")

    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: next(times),
        http_get=http_get,
        cache=MemoryFREDCache(),
        sleeper=lambda delay: None,
        retrieval_policy=FREDRetrievalPolicy(
            fresh_for=timedelta(minutes=5),
            stale_if_error_for=timedelta(hours=2),
            max_attempts=2,
            backoff_seconds=0,
        ),
    )

    live = provider.fetch(_query())[0]
    stale = provider.fetch(_query())[0]

    assert live.provenance.quality_state is DataQualityState.LIVE
    assert (
        stale.provenance.quality_state
        is DataQualityState.STALE
    )
    assert (
        stale.provenance.retrieved_at
        == live.provenance.retrieved_at
    )
    assert calls == 3


def test_expired_cache_cannot_mask_provider_failure() -> None:
    times = iter(
        [
            datetime(2026, 7, 16, 12, tzinfo=timezone.utc),
            datetime(2026, 7, 16, 15, tzinfo=timezone.utc),
        ]
    )
    calls = 0

    def http_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return SuccessfulResponse()
        raise requests.Timeout("offline")

    provider = FREDProvider(
        api_key="test-key",
        clock=lambda: next(times),
        http_get=http_get,
        cache=MemoryFREDCache(),
        sleeper=lambda delay: None,
        retrieval_policy=FREDRetrievalPolicy(
            fresh_for=timedelta(minutes=5),
            stale_if_error_for=timedelta(hours=2),
            max_attempts=1,
            backoff_seconds=0,
        ),
    )

    provider.fetch(_query())

    with pytest.raises(FREDProviderError, match="offline"):
        provider.fetch(_query())
