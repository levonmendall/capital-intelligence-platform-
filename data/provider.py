"""Provider-neutral contracts for point-in-time observation retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from data.observation import (
    DataFrequency,
    NormalizedObservation,
    Transformation,
)


class ProviderError(RuntimeError):
    """Base error for unavailable or invalid provider data."""


@dataclass(frozen=True, slots=True)
class SeriesSpecification:
    """Canonical meaning assigned to one provider series."""

    provider_series_identifier: str
    indicator: str
    category: str
    unit: str
    frequency: DataFrequency
    transformation: Transformation = Transformation.LEVEL
    stale_after: timedelta | None = None
    importance: float = 1.0

    def __post_init__(self) -> None:
        for field_name in (
            "provider_series_identifier",
            "indicator",
            "category",
            "unit",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{field_name} cannot be empty")
            object.__setattr__(self, field_name, normalized)

        if not isinstance(self.frequency, DataFrequency):
            raise TypeError("frequency must be a DataFrequency")
        if not isinstance(self.transformation, Transformation):
            raise TypeError(
                "transformation must be a Transformation"
            )
        if self.stale_after is not None:
            if not isinstance(self.stale_after, timedelta):
                raise TypeError(
                    "stale_after must be a timedelta or None"
                )
            if self.stale_after <= timedelta(0):
                raise ValueError(
                    "stale_after must be greater than zero"
                )
        if isinstance(self.importance, bool) or not isinstance(
            self.importance,
            (int, float),
        ):
            raise TypeError("importance must be numeric")
        if not 0.0 <= float(self.importance) <= 1.0:
            raise ValueError(
                "importance must be between 0.0 and 1.0"
            )
        object.__setattr__(
            self,
            "importance",
            float(self.importance),
        )


@dataclass(frozen=True, slots=True)
class ObservationQuery:
    """Point-in-time request for one canonical provider series."""

    series: SeriesSpecification
    as_of: datetime
    limit: int = 24

    def __post_init__(self) -> None:
        if not isinstance(self.series, SeriesSpecification):
            raise TypeError(
                "series must be a SeriesSpecification"
            )
        if not isinstance(self.as_of, datetime):
            raise TypeError("as_of must be a datetime")
        if (
            self.as_of.tzinfo is None
            or self.as_of.utcoffset() is None
        ):
            raise ValueError("as_of must be timezone-aware")
        if isinstance(self.limit, bool) or not isinstance(
            self.limit,
            int,
        ):
            raise TypeError("limit must be an int")
        if not 1 <= self.limit <= 100_000:
            raise ValueError(
                "limit must be between 1 and 100000"
            )


@runtime_checkable
class ObservationProvider(Protocol):
    """Provider capable of returning canonical point-in-time observations."""

    @property
    def name(self) -> str:
        """Stable provider identifier."""

    def fetch(
        self,
        query: ObservationQuery,
    ) -> tuple[NormalizedObservation, ...]:
        """Return observations available for the requested query."""
