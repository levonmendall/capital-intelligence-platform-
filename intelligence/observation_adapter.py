"""Compatibility adapter from legacy intelligence observations."""

from __future__ import annotations

from datetime import date, timedelta

from data import (
    DataFrequency,
    NormalizedObservation,
    ObservationProvenance,
    ObservationTrend,
    Transformation,
)
from intelligence.observation import Observation, Trend


_TREND_MAP = {
    Trend.RISING: ObservationTrend.RISING,
    Trend.FALLING: ObservationTrend.FALLING,
    Trend.STABLE: ObservationTrend.STABLE,
}


def to_normalized_observation(
    observation: Observation,
    *,
    provenance: ObservationProvenance,
    observation_date: date,
    frequency: DataFrequency,
    transformation: Transformation = Transformation.LEVEL,
    normalized_score: float | None = None,
    stale_after: timedelta | None = None,
) -> NormalizedObservation:
    """Convert one legacy observation using explicit provenance."""

    if not isinstance(observation, Observation):
        raise TypeError("observation must be an Observation")

    return NormalizedObservation(
        indicator=observation.indicator,
        category=observation.category.value,
        value=observation.value,
        previous_value=observation.previous_value,
        normalized_score=normalized_score,
        unit=observation.unit or "unspecified",
        frequency=frequency,
        observation_date=observation_date,
        provenance=provenance,
        transformation=transformation,
        trend=_TREND_MAP[observation.trend],
        importance=observation.importance,
        stale_after=stale_after,
    )
