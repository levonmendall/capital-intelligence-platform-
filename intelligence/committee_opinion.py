"""Committee opinion models for investment-governance decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable, Iterator


class CommitteeVote(str, Enum):
    """Available votes for an investment-committee member."""

    STRONGLY_APPROVE = "strongly_approve"
    APPROVE = "approve"
    NEUTRAL = "neutral"
    OBJECT = "object"
    STRONGLY_OBJECT = "strongly_object"

    @property
    def is_supportive(self) -> bool:
        return self in {
            CommitteeVote.STRONGLY_APPROVE,
            CommitteeVote.APPROVE,
        }

    @property
    def is_opposed(self) -> bool:
        return self in {
            CommitteeVote.OBJECT,
            CommitteeVote.STRONGLY_OBJECT,
        }


class CommitteeRole(str, Enum):
    """Functional roles represented on the investment committee."""

    MACRO = "macro"
    RISK = "risk"
    VALUATION = "valuation"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    TECHNICAL = "technical"


def _validate_text(
    value: object,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()

    if not allow_empty and not normalized:
        raise ValueError(f"{field_name} cannot be empty")

    return normalized


def _normalize_text_tuple(
    values: Iterable[str],
    *,
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, str):
        raise TypeError(
            f"{field_name} must be an iterable of strings, not a string"
        )

    normalized: list[str] = []

    try:
        iterator = iter(values)
    except TypeError as exc:
        raise TypeError(
            f"{field_name} must be an iterable of strings"
        ) from exc

    for index, value in enumerate(iterator):
        item = _validate_text(
            value,
            field_name=f"{field_name}[{index}]",
        )
        normalized.append(item)

    return tuple(normalized)


@dataclass(frozen=True, slots=True)
class CommitteeOpinion:
    """A committee member's formal opinion on one recommendation."""

    recommendation_identifier: str
    member: CommitteeRole
    vote: CommitteeVote
    confidence: float
    rationale: str
    strengths: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    suggested_changes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        recommendation_identifier = _validate_text(
            self.recommendation_identifier,
            field_name="recommendation_identifier",
        )

        if not isinstance(self.member, CommitteeRole):
            raise TypeError("member must be a CommitteeRole")

        if not isinstance(self.vote, CommitteeVote):
            raise TypeError("vote must be a CommitteeVote")

        if isinstance(self.confidence, bool) or not isinstance(
            self.confidence,
            (int, float),
        ):
            raise TypeError("confidence must be numeric")

        confidence = float(self.confidence)

        if not isfinite(confidence):
            raise ValueError("confidence must be finite")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        rationale = _validate_text(
            self.rationale,
            field_name="rationale",
        )

        strengths = _normalize_text_tuple(
            self.strengths,
            field_name="strengths",
        )
        concerns = _normalize_text_tuple(
            self.concerns,
            field_name="concerns",
        )
        suggested_changes = _normalize_text_tuple(
            self.suggested_changes,
            field_name="suggested_changes",
        )

        object.__setattr__(
            self,
            "recommendation_identifier",
            recommendation_identifier,
        )
        object.__setattr__(
            self,
            "confidence",
            round(confidence, 4),
        )
        object.__setattr__(
            self,
            "rationale",
            rationale,
        )
        object.__setattr__(
            self,
            "strengths",
            strengths,
        )
        object.__setattr__(
            self,
            "concerns",
            concerns,
        )
        object.__setattr__(
            self,
            "suggested_changes",
            suggested_changes,
        )

    @property
    def is_supportive(self) -> bool:
        return self.vote.is_supportive

    @property
    def is_opposed(self) -> bool:
        return self.vote.is_opposed

    @property
    def requires_revision(self) -> bool:
        return bool(self.suggested_changes)

    @property
    def has_concerns(self) -> bool:
        return bool(self.concerns)

    def summary(self) -> str:
        return (
            f"{self.member.value}: {self.vote.value} | "
            f"Confidence {self.confidence:.2%} | "
            f"{len(self.strengths)} strengths | "
            f"{len(self.concerns)} concerns | "
            f"{len(self.suggested_changes)} changes"
        )


@dataclass(frozen=True, slots=True)
class CommitteeOpinionSet:
    """Immutable collection of committee opinions."""

    opinions: tuple[CommitteeOpinion, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.opinions, CommitteeOpinion):
            raise TypeError(
                "opinions must be an iterable of CommitteeOpinion objects"
            )

        try:
            opinions = tuple(self.opinions)
        except TypeError as exc:
            raise TypeError(
                "opinions must be an iterable of CommitteeOpinion objects"
            ) from exc

        for index, opinion in enumerate(opinions):
            if not isinstance(opinion, CommitteeOpinion):
                raise TypeError(
                    f"opinions[{index}] must be a CommitteeOpinion"
                )

        identifiers = {
            opinion.recommendation_identifier
            for opinion in opinions
        }

        if len(identifiers) > 1:
            raise ValueError(
                "all opinions must reference the same recommendation"
            )

        roles = [opinion.member for opinion in opinions]

        if len(set(roles)) != len(roles):
            raise ValueError(
                "CommitteeOpinionSet cannot contain duplicate member roles"
            )

        object.__setattr__(self, "opinions", opinions)

    def __iter__(self) -> Iterator[CommitteeOpinion]:
        return iter(self.opinions)

    def __len__(self) -> int:
        return len(self.opinions)

    def __getitem__(self, index: int) -> CommitteeOpinion:
        return self.opinions[index]

    def __bool__(self) -> bool:
        return bool(self.opinions)

    @property
    def recommendation_identifier(self) -> str | None:
        if not self.opinions:
            return None

        return self.opinions[0].recommendation_identifier

    @property
    def supportive(self) -> tuple[CommitteeOpinion, ...]:
        return tuple(
            opinion
            for opinion in self.opinions
            if opinion.is_supportive
        )

    @property
    def opposed(self) -> tuple[CommitteeOpinion, ...]:
        return tuple(
            opinion
            for opinion in self.opinions
            if opinion.is_opposed
        )

    @property
    def neutral(self) -> tuple[CommitteeOpinion, ...]:
        return tuple(
            opinion
            for opinion in self.opinions
            if opinion.vote == CommitteeVote.NEUTRAL
        )

    @property
    def average_confidence(self) -> float:
        if not self.opinions:
            return 0.0

        return round(
            sum(
                opinion.confidence
                for opinion in self.opinions
            )
            / len(self.opinions),
            4,
        )

    @property
    def has_strong_objection(self) -> bool:
        return any(
            opinion.vote == CommitteeVote.STRONGLY_OBJECT
            for opinion in self.opinions
        )

    @property
    def requires_revision(self) -> bool:
        return any(
            opinion.requires_revision
            for opinion in self.opinions
        )

    def by_role(
        self,
        role: CommitteeRole,
    ) -> CommitteeOpinion | None:
        if not isinstance(role, CommitteeRole):
            raise TypeError("role must be a CommitteeRole")

        for opinion in self.opinions:
            if opinion.member == role:
                return opinion

        return None

    def summary(self) -> str:
        return (
            f"{len(self.opinions)} opinions | "
            f"{len(self.supportive)} supportive | "
            f"{len(self.neutral)} neutral | "
            f"{len(self.opposed)} opposed | "
            f"Average confidence {self.average_confidence:.2%}"
        )
