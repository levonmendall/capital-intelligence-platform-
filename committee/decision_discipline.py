"""Committee dissent and formal no-action decision contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite


class DissentDisposition(str, Enum):
    """Governance state of a recorded dissent."""

    OPEN = "open"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class NoActionReason(str, Enum):
    """Why the committee deliberately chose not to act."""

    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NO_EDGE = "no_edge"
    POLICY_BLOCK = "policy_block"
    RISK_REWARD = "risk_reward"
    WAIT_FOR_TRIGGER = "wait_for_trigger"
    DATA_QUALITY = "data_quality"
    OTHER = "other"


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
class StructuredDissent:
    """One minority position preserved without confidence averaging."""

    member: str
    specialty: str
    position: str
    rationale: str
    evidence_identifiers: tuple[str, ...]
    resolution_conditions: tuple[str, ...]
    materiality: float
    recorded_at: datetime
    disposition: DissentDisposition = DissentDisposition.OPEN

    def __post_init__(self) -> None:
        for field_name in (
            "member",
            "specialty",
            "position",
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
        for field_name in (
            "evidence_identifiers",
            "resolution_conditions",
        ):
            object.__setattr__(
                self,
                field_name,
                _text_tuple(
                    getattr(self, field_name),
                    field_name=field_name,
                    required=True,
                ),
            )
        if isinstance(self.materiality, bool) or not isinstance(
            self.materiality,
            (int, float),
        ):
            raise TypeError("materiality must be numeric")
        materiality = float(self.materiality)
        if not isfinite(materiality):
            raise ValueError("materiality must be finite")
        if not 0.0 <= materiality <= 1.0:
            raise ValueError(
                "materiality must be between 0.0 and 1.0"
            )
        object.__setattr__(
            self,
            "materiality",
            round(materiality, 4),
        )
        _aware_datetime(self.recorded_at, field_name="recorded_at")
        if not isinstance(
            self.disposition,
            DissentDisposition,
        ):
            raise TypeError(
                "disposition must be a DissentDisposition"
            )


@dataclass(frozen=True, slots=True)
class DissentRegister:
    """Structured minority views attached to one committee decision."""

    decision_identifier: str
    majority_view: str
    dissents: tuple[StructuredDissent, ...]

    def __post_init__(self) -> None:
        for field_name in ("decision_identifier", "majority_view"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        if not isinstance(self.dissents, tuple) or not all(
            isinstance(dissent, StructuredDissent)
            for dissent in self.dissents
        ):
            raise TypeError(
                "dissents must contain StructuredDissent values"
            )

    @property
    def unresolved(self) -> tuple[StructuredDissent, ...]:
        """Return dissent that remains open."""

        return tuple(
            dissent
            for dissent in self.dissents
            if dissent.disposition is DissentDisposition.OPEN
        )

    @property
    def material_unresolved(self) -> tuple[StructuredDissent, ...]:
        """Return open dissent with materiality of at least 0.5."""

        return tuple(
            dissent
            for dissent in self.unresolved
            if dissent.materiality >= 0.5
        )


@dataclass(frozen=True, slots=True)
class NoActionDecision:
    """A deliberate, reviewable decision not to change a portfolio."""

    decision_identifier: str
    reason: NoActionReason
    rationale: str
    decided_at: datetime
    review_at: datetime
    evidence_identifiers: tuple[str, ...]
    action_triggers: tuple[str, ...]
    recommendation_identifier: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "decision_identifier",
            _required_text(
                self.decision_identifier,
                field_name="decision_identifier",
            ),
        )
        if not isinstance(self.reason, NoActionReason):
            raise TypeError("reason must be a NoActionReason")
        object.__setattr__(
            self,
            "rationale",
            _required_text(self.rationale, field_name="rationale"),
        )
        decided_at = _aware_datetime(
            self.decided_at,
            field_name="decided_at",
        )
        review_at = _aware_datetime(
            self.review_at,
            field_name="review_at",
        )
        if review_at <= decided_at:
            raise ValueError(
                "review_at must be later than decided_at"
            )
        for field_name in (
            "evidence_identifiers",
            "action_triggers",
        ):
            object.__setattr__(
                self,
                field_name,
                _text_tuple(
                    getattr(self, field_name),
                    field_name=field_name,
                    required=True,
                ),
            )
        if self.recommendation_identifier is not None:
            object.__setattr__(
                self,
                "recommendation_identifier",
                _required_text(
                    self.recommendation_identifier,
                    field_name="recommendation_identifier",
                ),
            )
