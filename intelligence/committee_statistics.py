"""Analytical metrics for Investment Committee decisions."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

from intelligence.committee_opinion import (
    CommitteeRole,
    CommitteeVote,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)


@dataclass(frozen=True, slots=True)
class CommitteeStatistics:
    """Immutable analytical summary of one committee decision."""

    supportive_count: int
    neutral_count: int
    opposed_count: int

    support_ratio: float
    neutral_ratio: float
    opposition_ratio: float

    average_confidence: float
    confidence_std_dev: float

    agreement_score: float

    unanimous: bool
    split_decision: bool

    veto_count: int

    highest_confidence: float
    lowest_confidence: float

    highest_confidence_role: CommitteeRole | None
    lowest_confidence_role: CommitteeRole | None

    dissenting_roles: tuple[CommitteeRole, ...]

    def __post_init__(self) -> None:
        integer_fields = (
            "supportive_count",
            "neutral_count",
            "opposed_count",
            "veto_count",
        )

        for field in integer_fields:
            value = getattr(self, field)

            if not isinstance(value, int):
                raise TypeError(f"{field} must be an int")

            if value < 0:
                raise ValueError(f"{field} cannot be negative")

        for field in (
            "support_ratio",
            "neutral_ratio",
            "opposition_ratio",
            "average_confidence",
            "confidence_std_dev",
            "agreement_score",
            "highest_confidence",
            "lowest_confidence",
        ):
            value = getattr(self, field)

            if isinstance(value, bool):
                raise TypeError(f"{field} must be numeric")

            if not isinstance(value, (int, float)):
                raise TypeError(f"{field} must be numeric")

            value = float(value)

            if not isfinite(value):
                raise ValueError(f"{field} must be finite")

        if not isinstance(self.unanimous, bool):
            raise TypeError("unanimous must be bool")

        if not isinstance(self.split_decision, bool):
            raise TypeError("split_decision must be bool")

        if not isinstance(self.dissenting_roles, tuple):
            raise TypeError(
                "dissenting_roles must be a tuple"
            )

    @property
    def committee_size(self) -> int:
        return (
            self.supportive_count
            + self.neutral_count
            + self.opposed_count
        )

    @property
    def support_percentage(self) -> float:
        return self.support_ratio * 100.0

    @property
    def opposition_percentage(self) -> float:
        return self.opposition_ratio * 100.0


class CommitteeStatisticsCalculator:
    """Calculates analytical metrics for committee decisions."""

    def calculate(
        self,
        decision: InvestmentCommitteeDecision,
    ) -> CommitteeStatistics:

        if not isinstance(
            decision,
            InvestmentCommitteeDecision,
        ):
            raise TypeError(
                "decision must be an InvestmentCommitteeDecision"
            )

        opinions = tuple(decision.opinions)

        committee_size = len(opinions)

        if committee_size == 0:
            raise ValueError(
                "committee contains no opinions"
            )

        supportive = [
            opinion
            for opinion in opinions
            if opinion.vote.is_supportive
        ]

        neutral = [
            opinion
            for opinion in opinions
            if opinion.vote is CommitteeVote.NEUTRAL
        ]

        opposed = [
            opinion
            for opinion in opinions
            if opinion.vote.is_opposed
        ]

        confidences = [
            opinion.confidence
            for opinion in opinions
        ]

        average = (
            sum(confidences)
            / committee_size
        )

        variance = (
            sum(
                (value - average) ** 2
                for value in confidences
            )
            / committee_size
        )

        std_dev = sqrt(variance)

        highest = max(
            opinions,
            key=lambda opinion: opinion.confidence,
        )

        lowest = min(
            opinions,
            key=lambda opinion: opinion.confidence,
        )

        agreement_score = max(
            len(supportive),
            len(neutral),
            len(opposed),
        ) / committee_size

        unanimous = (
            len(supportive) == committee_size
            or len(neutral) == committee_size
            or len(opposed) == committee_size
        )

        split_decision = (
            len(supportive) > 0
            and len(opposed) > 0
        )

        majority_vote = max(
            (
                CommitteeVote.APPROVE,
                len(supportive),
            ),
            (
                CommitteeVote.NEUTRAL,
                len(neutral),
            ),
            (
                CommitteeVote.OBJECT,
                len(opposed),
            ),
            key=lambda item: item[1],
        )[0]

        dissenting_roles = tuple(
            opinion.member
            for opinion in opinions
            if (
                (majority_vote is CommitteeVote.APPROVE and not opinion.vote.is_supportive)
                or (majority_vote is CommitteeVote.NEUTRAL and opinion.vote is not CommitteeVote.NEUTRAL)
                or (majority_vote is CommitteeVote.OBJECT and not opinion.vote.is_opposed)
            )
        )

        return CommitteeStatistics(
            supportive_count=len(supportive),
            neutral_count=len(neutral),
            opposed_count=len(opposed),

            support_ratio=len(supportive)
            / committee_size,

            neutral_ratio=len(neutral)
            / committee_size,

            opposition_ratio=len(opposed)
            / committee_size,

            average_confidence=average,
            confidence_std_dev=std_dev,

            agreement_score=agreement_score,

            unanimous=unanimous,
            split_decision=split_decision,

            veto_count=len(decision.vetoes),

            highest_confidence=highest.confidence,
            lowest_confidence=lowest.confidence,

            highest_confidence_role=highest.member,
            lowest_confidence_role=lowest.member,

            dissenting_roles=dissenting_roles,
        )
