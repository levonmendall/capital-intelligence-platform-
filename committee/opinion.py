"""Opinion model used by the investment committee meeting layer.

This model is intentionally separate from
``intelligence.committee_opinion.CommitteeOpinion``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


def _required_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")

    return normalized


def _text_tuple(
    values: Iterable[str] | None,
    *,
    field_name: str,
) -> tuple[str, ...]:
    if values is None:
        return ()

    if isinstance(values, str):
        raise TypeError(
            f"{field_name} must be an iterable of strings"
        )

    try:
        supplied = tuple(values)
    except TypeError as exc:
        raise TypeError(
            f"{field_name} must be an iterable of strings"
        ) from exc

    return tuple(
        _required_text(
            value,
            field_name=f"{field_name}[{index}]",
        )
        for index, value in enumerate(supplied)
    )


def _confidence(value: object) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise TypeError("confidence must be numeric")

    normalized = float(value)

    if not isfinite(normalized):
        raise ValueError("confidence must be finite")

    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            "confidence must be between 0.0 and 1.0"
        )

    return round(normalized, 4)


@dataclass(frozen=True, slots=True)
class CommitteeOpinion:
    """Opinion submitted by a member during a committee meeting."""

    member: str
    specialty: str
    outlook: str
    confidence: float
    recommendation: str
    evidence: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    opportunities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "member",
            _required_text(
                self.member,
                field_name="member",
            ),
        )

        object.__setattr__(
            self,
            "specialty",
            _required_text(
                self.specialty,
                field_name="specialty",
            ),
        )

        object.__setattr__(
            self,
            "outlook",
            _required_text(
                self.outlook,
                field_name="outlook",
            ),
        )

        object.__setattr__(
            self,
            "confidence",
            _confidence(self.confidence),
        )

        object.__setattr__(
            self,
            "recommendation",
            _required_text(
                self.recommendation,
                field_name="recommendation",
            ),
        )

        object.__setattr__(
            self,
            "evidence",
            _text_tuple(
                self.evidence,
                field_name="evidence",
            ),
        )

        object.__setattr__(
            self,
            "risks",
            _text_tuple(
                self.risks,
                field_name="risks",
            ),
        )

        object.__setattr__(
            self,
            "opportunities",
            _text_tuple(
                self.opportunities,
                field_name="opportunities",
            ),
        )

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.75

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence)

    @property
    def has_risks(self) -> bool:
        return bool(self.risks)

    @property
    def has_opportunities(self) -> bool:
        return bool(self.opportunities)

    def summary(self) -> str:
        return (
            f"{self.member} ({self.specialty}) | "
            f"{self.recommendation} | "
            f"Confidence {self.confidence:.2%} | "
            f"Outlook: {self.outlook} | "
            f"{len(self.evidence)} evidence items | "
            f"{len(self.risks)} risks | "
            f"{len(self.opportunities)} opportunities"
        )


__all__ = [
    "CommitteeOpinion",
]
