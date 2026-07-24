"""Tests for canonical point-in-time observation contracts."""

from datetime import date, datetime, timedelta, timezone

import pytest

from data import (
    DataFrequency,
    DataQualityState,
    NormalizedObservation,
    ObservationProvenance,
    ObservationTrend,
    Transformation,
)
from intelligence.observation import (
    Observation,
    ObservationCategory,
    Trend,
)
from intelligence.observation_adapter import (
    to_normalized_observation,
)


RELEASED_AT = datetime(
    2026,
    7,
    10,
    12,
    tzinfo=timezone.utc,
)
RETRIEVED_AT = datetime(
    2026,
    7,
    10,
    12,
    5,
    tzinfo=timezone.utc,
)


def make_provenance(
    *,
    quality_state: DataQualityState = DataQualityState.LIVE,
    vintage_date: date | None = date(2026, 7, 10),
) -> ObservationProvenance:
    return ObservationProvenance(
        provider="FRED",
        series_identifier="UNRATE",
        released_at=RELEASED_AT,
        retrieved_at=RETRIEVED_AT,
        quality_state=quality_state,
        vintage_date=vintage_date,
    )


def make_observation(
    *,
    value: float | None = 4.1,
    quality_state: DataQualityState = DataQualityState.LIVE,
    vintage_date: date | None = date(2026, 7, 10),
) -> NormalizedObservation:
    return NormalizedObservation(
        indicator="unemployment",
        category="labor",
        value=value,
        previous_value=4.0,
        normalized_score=0.25,
        unit="percent",
        frequency=DataFrequency.MONTHLY,
        observation_date=date(2026, 6, 1),
        provenance=make_provenance(
            quality_state=quality_state,
            vintage_date=vintage_date,
        ),
        transformation=Transformation.LEVEL,
        trend=ObservationTrend.RISING,
        importance=0.9,
        stale_after=timedelta(days=45),
    )


def test_live_observation_is_immutable_and_serializable() -> None:
    observation = make_observation()
    payload = observation.to_dict()

    assert payload["provider"] == "FRED"
    assert payload["series_identifier"] == "UNRATE"
    assert payload["observation_date"] == "2026-06-01"
    assert payload["quality_state"] == "live"
    assert payload["released_at"].endswith("+00:00")
    assert observation.revision_key == (
        "FRED",
        "UNRATE",
        date(2026, 6, 1),
        date(2026, 7, 10),
    )


@pytest.mark.parametrize(
    "quality_state",
    [
        DataQualityState.LIVE,
        DataQualityState.CACHED,
        DataQualityState.STALE,
        DataQualityState.FIXTURE,
        DataQualityState.FALLBACK,
    ],
)
def test_non_missing_quality_states_round_trip(
    quality_state: DataQualityState,
) -> None:
    observation = make_observation(
        quality_state=quality_state,
    )

    assert (
        observation.to_dict()["quality_state"]
        == quality_state.value
    )


def test_point_in_time_availability_blocks_future_release() -> None:
    observation = make_observation()
    before_release = RELEASED_AT - timedelta(seconds=1)

    assert not observation.is_available_at(before_release)
    assert observation.is_available_at(RELEASED_AT)

    with pytest.raises(ValueError, match="not available"):
        observation.require_available_at(before_release)


def test_missing_observation_cannot_masquerade_as_zero() -> None:
    missing = make_observation(
        value=None,
        quality_state=DataQualityState.MISSING,
    )

    assert not missing.is_available_at(RETRIEVED_AT)

    with pytest.raises(
        ValueError,
        match="missing observations cannot contain a value",
    ):
        make_observation(
            value=0.0,
            quality_state=DataQualityState.MISSING,
        )


def test_non_missing_observation_requires_value() -> None:
    with pytest.raises(
        ValueError,
        match="non-missing observations require a value",
    ):
        make_observation(value=None)


def test_provenance_requires_aware_ordered_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ObservationProvenance(
            provider="FRED",
            series_identifier="UNRATE",
            released_at=datetime(2026, 7, 10, 12),
            retrieved_at=RETRIEVED_AT,
            quality_state=DataQualityState.LIVE,
        )

    with pytest.raises(ValueError, match="later than"):
        ObservationProvenance(
            provider="FRED",
            series_identifier="UNRATE",
            released_at=RETRIEVED_AT + timedelta(minutes=1),
            retrieved_at=RETRIEVED_AT,
            quality_state=DataQualityState.LIVE,
        )


def test_provenance_requires_provider_and_series_identity() -> None:
    with pytest.raises(ValueError, match="provider"):
        ObservationProvenance(
            provider=" ",
            series_identifier="UNRATE",
            released_at=RELEASED_AT,
            retrieved_at=RETRIEVED_AT,
            quality_state=DataQualityState.LIVE,
        )

    with pytest.raises(ValueError, match="series_identifier"):
        ObservationProvenance(
            provider="FRED",
            series_identifier="",
            released_at=RELEASED_AT,
            retrieved_at=RETRIEVED_AT,
            quality_state=DataQualityState.LIVE,
        )


def test_normalized_score_is_bounded() -> None:
    with pytest.raises(ValueError, match="normalized_score"):
        NormalizedObservation(
            indicator="unemployment",
            category="labor",
            value=4.1,
            normalized_score=1.01,
            unit="percent",
            frequency=DataFrequency.MONTHLY,
            observation_date=date(2026, 6, 1),
            provenance=make_provenance(),
        )


def test_vintages_have_distinct_revision_keys() -> None:
    first = make_observation(
        vintage_date=date(2026, 6, 15),
    )
    revised = make_observation(
        vintage_date=date(2026, 7, 10),
    )

    assert first.revision_key != revised.revision_key


def test_staleness_uses_explicit_state_or_threshold() -> None:
    observation = make_observation()

    assert not observation.is_stale_at(RETRIEVED_AT)
    assert observation.is_stale_at(
        RETRIEVED_AT + timedelta(days=46)
    )
    assert make_observation(
        quality_state=DataQualityState.STALE,
    ).is_stale_at(RETRIEVED_AT)


def test_legacy_adapter_requires_explicit_provenance() -> None:
    legacy = Observation(
        indicator="unemployment",
        category=ObservationCategory.LABOR,
        value=4.1,
        previous_value=4.0,
        trend=Trend.RISING,
        unit="percent",
        source="FRED",
        importance=0.9,
    )

    normalized = to_normalized_observation(
        legacy,
        provenance=make_provenance(),
        observation_date=date(2026, 6, 1),
        frequency=DataFrequency.MONTHLY,
        normalized_score=0.25,
    )

    assert normalized.indicator == legacy.indicator
    assert normalized.category == legacy.category.value
    assert normalized.trend is ObservationTrend.RISING
    assert normalized.provenance.provider == "FRED"
