"""Meeting-oriented investment committee opinion models.

This module belongs to the collective governance layer. It represents
the qualitative opinion submitted by an existing committee member
during an investment committee meeting.

It is intentionally distinct from:

    intelligence.committee_opinion

The intelligence model represents standardized specialist votes and
confidence assessments. This model supports the existing committee
meeting and consensus workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


def _normalize_required_text(
    value: object,
    *,
    field_name: str,
) -> str:
    """Validate and normalize required text."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")

    return normalized


def _normalize_optional_text(
    value: object,
    *,
    field_name: str,
) -> str:
    """Validate and normalize optional text."""

    if value is None:
        return ""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    return value.strip()


def _normalize_text_collection(
    values: Iterable[str] | None,
    *,
    field_name: str,
) -> tuple[str, ...]:
    """Convert a collection of text values into an immutable tuple."""

    if values is None:
        return ()

    if isinstance(values, str):
        raise TypeError(
            f"{field_name} must be an iterable of strings, not a string"
        )

    try:
        supplied_values = tuple(values)
    except TypeError as exc:
        raise TypeError(
            f"{field_name} must be an iterable of strings"
        ) from exc

    normalized: list[str] = []

    for index, value in enumerate(supplied_values):
        normalized.append(
            _normalize_required_text(
                value,
                field_name=f"{field_name}[{index}]",
            )
        )

    return tuple(normalized)


def _normalize_confidence(value: object) -> float:
    """Validate and normalize a confidence score."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be numeric")

    confidence = float(value)

    if not isfinite(confidence):
        raise ValueError("confidence must be finite")

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "confidence must be between 0.0 and 1.0"
        )

    return round(confidence, 4)


@dataclass(frozen=True, slots=True)
class CommitteeOpinion:
    """An opinion submitted during an investment committee meeting.

    Attributes:
        specialty:
            Committee member's area of expertise, such as Macro,
            Risk, Credit, or Valuation.

        recommendation:
            Concise recommendation or position supplied by the member.

        confidence:
            Confidence in the opinion, expressed from 0.0 through 1.0.

        rationale:
            Explanation supporting the recommendation.

        risks:
            Material risks identified by the member.

        opportunities:
            Material opportunities identified by the member.
    """

    specialty: str
    recommendation: str
    confidence: float
    rationale: str
    risks: tuple[str, ...] = ()
    opportunities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        specialty = _normalize_required_text(
            self.specialty,
            field_name="specialty",
        )

        recommendation = _normalize_required_text(
            self.recommendation,
            field_name="recommendation",
        )

        confidence = _normalize_confidence(
            self.confidence
        )

        rationale = _normalize_required_text(
            self.rationale,
            field_name="rationale",
        )

        risks = _normalize_text_collection(
            self.risks,
            field_name="risks",
        )

        opportunities = _normalize_text_collection(
            self.opportunities,
            field_name="opportunities",
        )

        object.__setattr__(
            self,
            "specialty",
            specialty,
        )
        object.__setattr__(
            self,
            "recommendation",
            recommendation,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "rationale",
            rationale,
        )
        object.__setattr__(
            self,
            "risks",
            risks,
        )
        object.__setattr__(
            self,
            "opportunities",
            opportunities,
        )

    @property
    def has_risks(self) -> bool:
        """Return whether the member identified material risks."""

        return bool(self.risks)

    @property
    def has_opportunities(self) -> bool:
        """Return whether the member identified opportunities."""

        return bool(self.opportunities)

    @property
    def is_high_confidence(self) -> bool:
        """Return whether confidence meets the high-confidence level."""

        return self.confidence >= 0.75

    def summary(self) -> str:
        """Return a deterministic meeting summary."""

        return (
            f"{self.specialty}: {self.recommendation} | "
            f"Confidence {self.confidence:.2%} | "
            f"{len(self.risks)} risks | "
            f"{len(self.opportunities)} opportunities"
        )


__all__ = [
    "CommitteeOpinion",
]
