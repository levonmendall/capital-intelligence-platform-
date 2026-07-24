"""Immutable point-in-time observation and provenance contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from math import isfinite
from typing import Any


class DataQualityState(str, Enum):
    """Operational state of an observation at retrieval time."""

    LIVE = "live"
    CACHED = "cached"
    STALE = "stale"
    FIXTURE = "fixture"
    FALLBACK = "fallback"
    MISSING = "missing"


class DataFrequency(str, Enum):
    """Publication frequency of a source series."""

    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    EVENT = "event"


class ObservationTrend(str, Enum):
    """Direction of change in a normalized observation."""

    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    UNKNOWN = "unknown"


class Transformation(str, Enum):
    """Transformation applied to a provider's source value."""

    LEVEL = "level"
    CHANGE = "change"
    PERCENT_CHANGE = "percent_change"
    MONTH_OVER_MONTH = "month_over_month"
    YEAR_OVER_YEAR = "year_over_year"
    ANNUALIZED = "annualized"
    NORMALIZED_SCORE = "normalized_score"
    OTHER = "other"


def _required_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _aware_datetime(
    value: object,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _date_only(value: object, *, field_name: str) -> date:
    if isinstance(value, datetime) or not isinstance(value, date):
        raise TypeError(f"{field_name} must be a date")
    return value


def _optional_number(
    value: object,
    *,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric or None")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{field_name} must be finite")
    return normalized


@dataclass(frozen=True, slots=True)
class ObservationProvenance:
    """Provider identity and availability metadata for one observation."""

    provider: str
    series_identifier: str
    released_at: datetime
    retrieved_at: datetime
    quality_state: DataQualityState
    vintage_date: date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider",
            _required_text(self.provider, field_name="provider"),
        )
        object.__setattr__(
            self,
            "series_identifier",
            _required_text(
                self.series_identifier,
                field_name="series_identifier",
            ),
        )
        released_at = _aware_datetime(
            self.released_at,
            field_name="released_at",
        )
        retrieved_at = _aware_datetime(
            self.retrieved_at,
            field_name="retrieved_at",
        )
        if released_at > retrieved_at:
            raise ValueError(
                "released_at cannot be later than retrieved_at"
            )
        if not isinstance(self.quality_state, DataQualityState):
            raise TypeError(
                "quality_state must be a DataQualityState"
            )
        if self.vintage_date is not None:
            vintage_date = _date_only(
                self.vintage_date,
                field_name="vintage_date",
            )
            if vintage_date > retrieved_at.date():
                raise ValueError(
                    "vintage_date cannot be later than retrieved_at"
                )

    @property
    def source_key(self) -> tuple[str, str]:
        """Return the stable provider-series identity."""

        return self.provider, self.series_identifier


@dataclass(frozen=True, slots=True)
class NormalizedObservation:
    """One immutable, auditable, point-in-time observation."""

    indicator: str
    category: str
    value: float | None
    unit: str
    frequency: DataFrequency
    observation_date: date
    provenance: ObservationProvenance
    transformation: Transformation = Transformation.LEVEL
    previous_value: float | None = None
    normalized_score: float | None = None
    trend: ObservationTrend = ObservationTrend.UNKNOWN
    importance: float = 1.0
    stale_after: timedelta | None = None

    def __post_init__(self) -> None:
        for field_name in ("indicator", "category", "unit"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        if not isinstance(self.frequency, DataFrequency):
            raise TypeError("frequency must be a DataFrequency")
        if not isinstance(self.provenance, ObservationProvenance):
            raise TypeError(
                "provenance must be ObservationProvenance"
            )
        if not isinstance(self.transformation, Transformation):
            raise TypeError(
                "transformation must be a Transformation"
            )
        if not isinstance(self.trend, ObservationTrend):
            raise TypeError("trend must be an ObservationTrend")

        observation_date = _date_only(
            self.observation_date,
            field_name="observation_date",
        )
        if observation_date > self.provenance.released_at.date():
            raise ValueError(
                "observation_date cannot be later than released_at"
            )
        if (
            self.provenance.vintage_date is not None
            and self.provenance.vintage_date < observation_date
        ):
            raise ValueError(
                "vintage_date cannot be earlier than observation_date"
            )

        value = _optional_number(self.value, field_name="value")
        previous_value = _optional_number(
            self.previous_value,
            field_name="previous_value",
        )
        normalized_score = _optional_number(
            self.normalized_score,
            field_name="normalized_score",
        )
        if (
            normalized_score is not None
            and not -1.0 <= normalized_score <= 1.0
        ):
            raise ValueError(
                "normalized_score must be between -1.0 and 1.0"
            )

        if isinstance(self.importance, bool) or not isinstance(
            self.importance,
            (int, float),
        ):
            raise TypeError("importance must be numeric")
        importance = float(self.importance)
        if not isfinite(importance):
            raise ValueError("importance must be finite")
        if not 0.0 <= importance <= 1.0:
            raise ValueError(
                "importance must be between 0.0 and 1.0"
            )

        is_missing = (
            self.provenance.quality_state
            is DataQualityState.MISSING
        )
        if is_missing and value is not None:
            raise ValueError(
                "missing observations cannot contain a value"
            )
        if not is_missing and value is None:
            raise ValueError(
                "non-missing observations require a value"
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

        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "previous_value",
            previous_value,
        )
        object.__setattr__(
            self,
            "normalized_score",
            normalized_score,
        )
        object.__setattr__(self, "importance", importance)

    @property
    def revision_key(
        self,
    ) -> tuple[str, str, date, date | None]:
        """Return identity fields that distinguish historical vintages."""

        return (
            *self.provenance.source_key,
            self.observation_date,
            self.provenance.vintage_date,
        )

    def is_available_at(self, as_of: datetime) -> bool:
        """Whether the observation was knowable at a decision timestamp."""

        resolved = _aware_datetime(as_of, field_name="as_of")
        return (
            self.provenance.quality_state
            is not DataQualityState.MISSING
            and self.provenance.released_at <= resolved
        )

    def require_available_at(self, as_of: datetime) -> None:
        """Raise when a point-in-time consumer would use future data."""

        if not self.is_available_at(as_of):
            raise ValueError(
                "observation was not available at the requested time"
            )

    def is_stale_at(self, as_of: datetime) -> bool:
        """Whether the observation is explicitly or temporally stale."""

        resolved = _aware_datetime(as_of, field_name="as_of")
        if (
            self.provenance.quality_state
            is DataQualityState.STALE
        ):
            return True
        if self.stale_after is None:
            return False
        return (
            self.provenance.retrieved_at + self.stale_after
            < resolved
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-ready representation."""

        return {
            "indicator": self.indicator,
            "category": self.category,
            "value": self.value,
            "previous_value": self.previous_value,
            "normalized_score": self.normalized_score,
            "unit": self.unit,
            "frequency": self.frequency.value,
            "observation_date": self.observation_date.isoformat(),
            "provider": self.provenance.provider,
            "series_identifier": (
                self.provenance.series_identifier
            ),
            "released_at": (
                self.provenance.released_at.isoformat()
            ),
            "retrieved_at": (
                self.provenance.retrieved_at.isoformat()
            ),
            "quality_state": (
                self.provenance.quality_state.value
            ),
            "vintage_date": (
                self.provenance.vintage_date.isoformat()
                if self.provenance.vintage_date is not None
                else None
            ),
            "transformation": self.transformation.value,
            "trend": self.trend.value,
            "importance": self.importance,
            "stale_after_seconds": (
                self.stale_after.total_seconds()
                if self.stale_after is not None
                else None
            ),
        }
