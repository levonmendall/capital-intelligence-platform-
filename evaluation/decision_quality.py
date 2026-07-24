"""Separate decision-process quality from realized outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProcessVerdict(str, Enum):
    """Explicit reviewer conclusion about decision discipline."""

    DISCIPLINED = "disciplined"
    FLAWED = "flawed"
    UNRESOLVED = "unresolved"


class DecisionOutcome(str, Enum):
    """Realized result without implying process quality."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    FLAT = "flat"
    UNRESOLVED = "unresolved"


class DecisionQualityClassification(str, Enum):
    """Process-outcome quadrant used by the decision ledger."""

    DISCIPLINED_POSITIVE = "disciplined_positive"
    DISCIPLINED_NEGATIVE = "disciplined_negative"
    FLAWED_POSITIVE = "flawed_positive"
    FLAWED_NEGATIVE = "flawed_negative"
    INCONCLUSIVE = "inconclusive"


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
class DecisionQualityReview:
    """Immutable review of process and outcome for one decision."""

    decision_identifier: str
    reviewed_at: datetime
    process_verdict: ProcessVerdict
    outcome: DecisionOutcome
    process_evidence: tuple[str, ...]
    outcome_evidence: tuple[str, ...]
    lessons: tuple[str, ...]
    reviewer: str

    def __post_init__(self) -> None:
        for field_name in ("decision_identifier", "reviewer"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        _aware_datetime(self.reviewed_at, field_name="reviewed_at")
        if not isinstance(self.process_verdict, ProcessVerdict):
            raise TypeError(
                "process_verdict must be a ProcessVerdict"
            )
        if not isinstance(self.outcome, DecisionOutcome):
            raise TypeError(
                "outcome must be a DecisionOutcome"
            )
        for field_name in (
            "process_evidence",
            "outcome_evidence",
            "lessons",
        ):
            object.__setattr__(
                self,
                field_name,
                _text_tuple(
                    getattr(self, field_name),
                    field_name=field_name,
                    required=field_name != "lessons",
                ),
            )

    @property
    def classification(self) -> DecisionQualityClassification:
        """Return the process-outcome quadrant without conflation."""

        mapping = {
            (
                ProcessVerdict.DISCIPLINED,
                DecisionOutcome.POSITIVE,
            ): DecisionQualityClassification.DISCIPLINED_POSITIVE,
            (
                ProcessVerdict.DISCIPLINED,
                DecisionOutcome.NEGATIVE,
            ): DecisionQualityClassification.DISCIPLINED_NEGATIVE,
            (
                ProcessVerdict.FLAWED,
                DecisionOutcome.POSITIVE,
            ): DecisionQualityClassification.FLAWED_POSITIVE,
            (
                ProcessVerdict.FLAWED,
                DecisionOutcome.NEGATIVE,
            ): DecisionQualityClassification.FLAWED_NEGATIVE,
        }
        return mapping.get(
            (self.process_verdict, self.outcome),
            DecisionQualityClassification.INCONCLUSIVE,
        )
