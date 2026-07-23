"""Meeting-oriented investment committee opinion models.

This module belongs to the collective committee-governance layer.

It is intentionally distinct from ``intelligence.committee_opinion``,
which represents standardized analytical votes produced by specialist
intelligence committee members.

This model preserves compatibility with the existing investment
committee workflow.
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


def _member_specialty(member: object) -> str:
    for attribute_name in (
        "specialty",
        "display_name",
        "name",
        "role",
    ):
        value = getattr(member, attribute_name, None)

        if value is None:
            continue

        enum_value = getattr(value, "value", value)

        if isinstance(enum_value, str) and enum_value.strip():
            return enum_value.strip()

    if isinstance(member, str) and member.strip():
        return member.strip()

    return member.__class__.__name__


@dataclass(frozen=True, slots=True, init=False)
class CommitteeOpinion:
    """An opinion submitted during an investment committee meeting."""

    member: object
    recommendation: str
    confidence: float
    rationale: str
    outlook: str
    risks: tuple[str, ...]
    opportunities: tuple[str, ...]
    _specialty: str

    def __init__(
        self,
        *,
        recommendation: str,
        confidence: float,
        rationale: str,
        member: object | None = None,
        specialty: str | None = None,
        outlook: str | None = None,
        risks: Iterable[str] | None = None,
        opportunities: Iterable[str] | None = None,
    ) -> None:
        if member is None and specialty is None:
            raise ValueError(
                "either member or specialty must be provided"
            )

        if specialty is not None:
            normalized_specialty = _normalize_required_text(
                specialty,
                field_name="specialty",
            )
        else:
            normalized_specialty = _member_specialty(member)

        if member is not None and specialty is not None:
            derived_specialty = _member_specialty(member)

            if (
                derived_specialty.casefold()
                != normalized_specialty.casefold()
            ):
                raise ValueError(
                    "member and specialty describe different "
                    "committee roles"
                )

        if member is None:
            member = normalized_specialty

        object.__setattr__(
            self,
            "member",
            member,
        )
        object.__setattr__(
            self,
            "recommendation",
            _normalize_required_text(
                recommendation,
                field_name="recommendation",
            ),
        )
        object.__setattr__(
            self,
            "confidence",
            _normalize_confidence(confidence),
        )
        object.__setattr__(
            self,
            "rationale",
            _normalize_required_text(
                rationale,
                field_name="rationale",
            ),
        )
        object.__setattr__(
            self,
            "outlook",
            _normalize_optional_text(
                outlook,
                field_name="outlook",
            ),
        )
        object.__setattr__(
            self,
            "risks",
            _normalize_text_collection(
                risks,
                field_name="risks",
            ),
        )
        object.__setattr__(
            self,
            "opportunities",
            _normalize_text_collection(
                opportunities,
                field_name="opportunities",
            ),
        )
        object.__setattr__(
            self,
            "_specialty",
            normalized_specialty,
        )

    @property
    def specialty(self) -> str:
        return self._specialty

    @property
    def has_risks(self) -> bool:
        return bool(self.risks)

    @property
    def has_opportunities(self) -> bool:
        return bool(self.opportunities)

    @property
    def has_outlook(self) -> bool:
        return bool(self.outlook)

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.75

    def summary(self) -> str:
        outlook_text = (
            f" | Outlook {self.outlook}"
            if self.outlook
            else ""
        )

        return (
            f"{self.specialty}: {self.recommendation} | "
            f"Confidence {self.confidence:.2%}"
            f"{outlook_text} | "
            f"{len(self.risks)} risks | "
            f"{len(self.opportunities)} opportunities"
        )


__all__ = [
    "CommitteeOpinion",
]
