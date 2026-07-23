"""Domain models for investment committee opinions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CommitteeVote(str, Enum):
    """Possible committee votes."""

    STRONGLY_APPROVE = "strongly_approve"
    APPROVE = "approve"
    NEUTRAL = "neutral"
    OBJECT = "object"
    STRONGLY_OBJECT = "strongly_object"


class CommitteeRole(str, Enum):
    """Committee member specialization."""

    MACRO = "macro"
    RISK = "risk"
    VALUATION = "valuation"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    TECHNICAL = "technical"


@dataclass(frozen=True)
class CommitteeOpinion:
    """
    Opinion issued by one committee member regarding one recommendation.
    """

    recommendation_identifier: str

    member: CommitteeRole

    vote: CommitteeVote

    confidence: float

    rationale: str

    strengths: tuple[str, ...]

    concerns: tuple[str, ...]

    suggested_changes: tuple[str, ...]

    def __post_init__(self) -> None:

        if not self.recommendation_identifier.strip():
            raise ValueError(
                "recommendation_identifier cannot be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

        if not self.rationale.strip():
            raise ValueError(
                "rationale cannot be empty"
            )


@dataclass(frozen=True)
class CommitteeOpinionSet:
    """
    Collection of committee opinions.
    """

    opinions: tuple[CommitteeOpinion, ...]

    confidence: float

    summary: str

    def __post_init__(self) -> None:

        if not self.opinions:
            raise ValueError(
                "opinions cannot be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

        if not self.summary.strip():
            raise ValueError(
                "summary cannot be empty"
            )

    def by_member(
        self,
        member: CommitteeRole,
    ) -> tuple[CommitteeOpinion, ...]:

        return tuple(
            opinion
            for opinion in self.opinions
            if opinion.member == member
        )

    def by_recommendation(
        self,
        recommendation_identifier: str,
    ) -> tuple[CommitteeOpinion, ...]:

        return tuple(
            opinion
            for opinion in self.opinions
            if opinion.recommendation_identifier
            == recommendation_identifier
        )
