"""Decision-discipline models for theses, evidence, and scenarios."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from math import isfinite


class ThesisLifecycleStatus(str, Enum):
    """Governed states of an investment thesis."""

    PROPOSED = "proposed"
    ACTIVE = "active"
    CHALLENGED = "challenged"
    INVALIDATED = "invalidated"
    CLOSED = "closed"


class TriggerType(str, Enum):
    """Evidence domain capable of falsifying a thesis."""

    PRICE = "price"
    VALUATION = "valuation"
    MACRO = "macro"
    FUNDAMENTAL = "fundamental"
    MARKET_STRUCTURE = "market_structure"
    DATA_QUALITY = "data_quality"
    DATE = "date"
    OTHER = "other"


class TriggerComparator(str, Enum):
    """Deterministic comparison applied to a trigger metric."""

    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"
    CHANGED = "changed"
    MANUAL_REVIEW = "manual_review"


class EvidenceTrustLevel(str, Enum):
    """Human-readable trust band derived from explicit dimensions."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ShockDirection(str, Enum):
    """Direction of a scenario shock."""

    RISE = "rise"
    FALL = "fall"
    WIDEN = "widen"
    NARROW = "narrow"
    UNAVAILABLE = "unavailable"
    OTHER = "other"


class TransmissionDirection(str, Enum):
    """Expected directional relationship between two factors."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NONLINEAR = "nonlinear"
    UNKNOWN = "unknown"


def _required_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _aware_datetime(value: object, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _score(value: object, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{field_name} must be finite")
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            f"{field_name} must be between 0.0 and 1.0"
        )
    return round(normalized, 4)


def _text_tuple(
    values: object,
    *,
    field_name: str,
    required: bool = False,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(
        _required_text(value, field_name=field_name)
        for value in values
    )
    if required and not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


@dataclass(frozen=True, slots=True)
class FalsificationTrigger:
    """One explicit condition that challenges or invalidates a thesis."""

    identifier: str
    trigger_type: TriggerType
    description: str
    metric: str
    comparator: TriggerComparator
    threshold: float | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("identifier", "description", "metric"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if not isinstance(self.trigger_type, TriggerType):
            raise TypeError(
                "trigger_type must be a TriggerType"
            )
        if not isinstance(self.comparator, TriggerComparator):
            raise TypeError(
                "comparator must be a TriggerComparator"
            )
        if self.threshold is not None:
            if isinstance(self.threshold, bool) or not isinstance(
                self.threshold,
                (int, float),
            ):
                raise TypeError(
                    "threshold must be numeric or None"
                )
            threshold = float(self.threshold)
            if not isfinite(threshold):
                raise ValueError("threshold must be finite")
            object.__setattr__(self, "threshold", threshold)
        if self.comparator in {
            TriggerComparator.ABOVE,
            TriggerComparator.BELOW,
            TriggerComparator.EQUALS,
        } and self.threshold is None:
            raise ValueError(
                "numeric comparators require a threshold"
            )
        if self.unit is not None:
            object.__setattr__(
                self,
                "unit",
                _required_text(self.unit, field_name="unit"),
            )


@dataclass(frozen=True, slots=True)
class ThesisTransition:
    """One append-only thesis status transition."""

    from_status: ThesisLifecycleStatus
    to_status: ThesisLifecycleStatus
    changed_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.from_status,
            ThesisLifecycleStatus,
        ) or not isinstance(self.to_status, ThesisLifecycleStatus):
            raise TypeError(
                "transition statuses must be ThesisLifecycleStatus"
            )
        _aware_datetime(self.changed_at, field_name="changed_at")
        object.__setattr__(
            self,
            "reason",
            _required_text(self.reason, field_name="reason"),
        )


@dataclass(frozen=True, slots=True)
class ThesisLifecycle:
    """Immutable lifecycle and falsification policy for one thesis."""

    thesis_identifier: str
    status: ThesisLifecycleStatus
    opened_at: datetime
    review_at: datetime
    falsification_triggers: tuple[FalsificationTrigger, ...]
    transitions: tuple[ThesisTransition, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "thesis_identifier",
            _required_text(
                self.thesis_identifier,
                field_name="thesis_identifier",
            ),
        )
        if not isinstance(self.status, ThesisLifecycleStatus):
            raise TypeError(
                "status must be a ThesisLifecycleStatus"
            )
        opened_at = _aware_datetime(
            self.opened_at,
            field_name="opened_at",
        )
        review_at = _aware_datetime(
            self.review_at,
            field_name="review_at",
        )
        if review_at <= opened_at:
            raise ValueError(
                "review_at must be later than opened_at"
            )
        if (
            not isinstance(self.falsification_triggers, tuple)
            or not self.falsification_triggers
            or not all(
                isinstance(trigger, FalsificationTrigger)
                for trigger in self.falsification_triggers
            )
        ):
            raise ValueError(
                "falsification_triggers must contain triggers"
            )
        trigger_ids = tuple(
            trigger.identifier
            for trigger in self.falsification_triggers
        )
        if len(trigger_ids) != len(set(trigger_ids)):
            raise ValueError(
                "falsification trigger identifiers must be unique"
            )
        if not isinstance(self.transitions, tuple) or not all(
            isinstance(transition, ThesisTransition)
            for transition in self.transitions
        ):
            raise TypeError(
                "transitions must contain ThesisTransition values"
            )
        if self.transitions:
            if self.transitions[-1].to_status is not self.status:
                raise ValueError(
                    "latest transition must match lifecycle status"
                )
            if any(
                transition.changed_at < opened_at
                for transition in self.transitions
            ):
                raise ValueError(
                    "transitions cannot predate opened_at"
                )

    def transition(
        self,
        to_status: ThesisLifecycleStatus,
        *,
        changed_at: datetime,
        reason: str,
    ) -> ThesisLifecycle:
        """Return a new lifecycle after a valid governed transition."""

        if not isinstance(to_status, ThesisLifecycleStatus):
            raise TypeError(
                "to_status must be a ThesisLifecycleStatus"
            )
        allowed = {
            ThesisLifecycleStatus.PROPOSED: {
                ThesisLifecycleStatus.ACTIVE,
                ThesisLifecycleStatus.CLOSED,
            },
            ThesisLifecycleStatus.ACTIVE: {
                ThesisLifecycleStatus.CHALLENGED,
                ThesisLifecycleStatus.INVALIDATED,
                ThesisLifecycleStatus.CLOSED,
            },
            ThesisLifecycleStatus.CHALLENGED: {
                ThesisLifecycleStatus.ACTIVE,
                ThesisLifecycleStatus.INVALIDATED,
                ThesisLifecycleStatus.CLOSED,
            },
            ThesisLifecycleStatus.INVALIDATED: {
                ThesisLifecycleStatus.CLOSED,
            },
            ThesisLifecycleStatus.CLOSED: set(),
        }
        if to_status not in allowed[self.status]:
            raise ValueError(
                f"cannot transition from {self.status.value} "
                f"to {to_status.value}"
            )
        changed_at = _aware_datetime(
            changed_at,
            field_name="changed_at",
        )
        prior_at = (
            self.transitions[-1].changed_at
            if self.transitions
            else self.opened_at
        )
        if changed_at < prior_at:
            raise ValueError(
                "changed_at cannot precede lifecycle history"
            )
        transition = ThesisTransition(
            from_status=self.status,
            to_status=to_status,
            changed_at=changed_at,
            reason=reason,
        )
        return replace(
            self,
            status=to_status,
            transitions=(*self.transitions, transition),
        )


@dataclass(frozen=True, slots=True)
class EvidenceTrustAssessment:
    """Transparent data-trust dimensions for one evidence snapshot."""

    evidence_identifier: str
    source_quality: float
    freshness: float
    completeness: float
    point_in_time_integrity: float
    directness: float
    revision_stability: float
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_identifier",
            _required_text(
                self.evidence_identifier,
                field_name="evidence_identifier",
            ),
        )
        for field_name in (
            "source_quality",
            "freshness",
            "completeness",
            "point_in_time_integrity",
            "directness",
            "revision_stability",
        ):
            object.__setattr__(
                self,
                field_name,
                _score(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        object.__setattr__(
            self,
            "limitations",
            _text_tuple(
                self.limitations,
                field_name="limitations",
            ),
        )

    @property
    def score(self) -> float:
        """Return the disclosed equal-weight trust score."""

        values = (
            self.source_quality,
            self.freshness,
            self.completeness,
            self.point_in_time_integrity,
            self.directness,
            self.revision_stability,
        )
        return round(sum(values) / len(values), 4)

    @property
    def level(self) -> EvidenceTrustLevel:
        """Return the trust band for the explicit score."""

        if self.score >= 0.8:
            return EvidenceTrustLevel.HIGH
        if self.score >= 0.5:
            return EvidenceTrustLevel.MODERATE
        return EvidenceTrustLevel.LOW


@dataclass(frozen=True, slots=True)
class ScenarioShock:
    """One explicit assumption changed by a scenario."""

    factor: str
    direction: ShockDirection
    magnitude: str
    rationale: str

    def __post_init__(self) -> None:
        for field_name in ("factor", "magnitude", "rationale"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if not isinstance(self.direction, ShockDirection):
            raise TypeError(
                "direction must be a ShockDirection"
            )


@dataclass(frozen=True, slots=True)
class DecisionScenario:
    """Named scenario used to test a thesis or decision."""

    identifier: str
    title: str
    shocks: tuple[ScenarioShock, ...]
    assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("identifier", "title"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if (
            not isinstance(self.shocks, tuple)
            or not self.shocks
            or not all(
                isinstance(shock, ScenarioShock)
                for shock in self.shocks
            )
        ):
            raise ValueError(
                "shocks must contain ScenarioShock values"
            )
        object.__setattr__(
            self,
            "assumptions",
            _text_tuple(
                self.assumptions,
                field_name="assumptions",
                required=True,
            ),
        )


@dataclass(frozen=True, slots=True)
class TransmissionEdge:
    """One documented cross-asset transmission relationship."""

    source_factor: str
    target_factor: str
    direction: TransmissionDirection
    strength: float
    expected_lag: str
    rationale: str

    def __post_init__(self) -> None:
        for field_name in (
            "source_factor",
            "target_factor",
            "expected_lag",
            "rationale",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if self.source_factor == self.target_factor:
            raise ValueError(
                "transmission edge cannot reference itself"
            )
        if not isinstance(
            self.direction,
            TransmissionDirection,
        ):
            raise TypeError(
                "direction must be a TransmissionDirection"
            )
        object.__setattr__(
            self,
            "strength",
            _score(self.strength, field_name="strength"),
        )


@dataclass(frozen=True, slots=True)
class CrossAssetTransmissionMap:
    """Auditable set of cross-asset transmission assumptions."""

    identifier: str
    edges: tuple[TransmissionEdge, ...]
    version: str

    def __post_init__(self) -> None:
        for field_name in ("identifier", "version"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if (
            not isinstance(self.edges, tuple)
            or not self.edges
            or not all(
                isinstance(edge, TransmissionEdge)
                for edge in self.edges
            )
        ):
            raise ValueError(
                "edges must contain TransmissionEdge values"
            )
        keys = tuple(
            (edge.source_factor, edge.target_factor)
            for edge in self.edges
        )
        if len(keys) != len(set(keys)):
            raise ValueError(
                "transmission edges must be unique"
            )

    def downstream(
        self,
        source_factor: str,
    ) -> tuple[TransmissionEdge, ...]:
        """Return direct documented effects of one factor."""

        normalized = _required_text(
            source_factor,
            field_name="source_factor",
        )
        return tuple(
            edge
            for edge in self.edges
            if edge.source_factor == normalized
        )
