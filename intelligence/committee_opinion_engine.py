"""Engine that coordinates investment committee member evaluations."""

from __future__ import annotations

from collections import Counter

from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeOpinionSet,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
    RecommendationSet,
)


class CommitteeOpinionEngine:
    """
    Coordinates all committee members.

    Each recommendation is independently evaluated by every
    registered committee member.
    """

    def __init__(
        self,
        members: tuple[CommitteeMember, ...],
    ) -> None:

        if not members:
            raise ValueError(
                "At least one committee member is required."
            )

        self._members = members

    def generate(
        self,
        recommendations: RecommendationSet,
    ) -> CommitteeOpinionSet:

        self._validate(recommendations)

        opinions = self._generate_opinions(
            recommendations
        )

        confidence = self._calculate_confidence(
            opinions
        )

        summary = self._build_summary(
            opinions
        )

        return CommitteeOpinionSet(
            opinions=opinions,
            confidence=confidence,
            summary=summary,
        )

    @staticmethod
    def _validate(
        recommendations: RecommendationSet,
    ) -> None:

        if not isinstance(
            recommendations,
            RecommendationSet,
        ):
            raise TypeError(
                "recommendations must be a RecommendationSet"
            )

    def _generate_opinions(
        self,
        recommendations: RecommendationSet,
    ) -> tuple[CommitteeOpinion, ...]:

        opinions: list[CommitteeOpinion] = []

        for recommendation in recommendations.recommendations:

            for member in self._members:

                opinions.append(
                    member.evaluate(
                        recommendation
                    )
                )

        return tuple(opinions)

    @staticmethod
    def _calculate_confidence(
        opinions: tuple[CommitteeOpinion, ...],
    ) -> float:

        if not opinions:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for opinion in opinions:

            weight = 1.0

            weighted_sum += (
                opinion.confidence * weight
            )

            total_weight += weight

        return round(
            weighted_sum / total_weight,
            4,
        )

    @staticmethod
    def _build_summary(
        opinions: tuple[CommitteeOpinion, ...],
    ) -> str:

        member_counts = Counter(
            opinion.member
            for opinion in opinions
        )

        vote_counts = Counter(
            opinion.vote
            for opinion in opinions
        )

        lines = [
            "Committee Opinion Summary",
            "",
            f"Total Opinions: {len(opinions)}",
            "",
            "Votes",
        ]

        for vote, count in sorted(
            vote_counts.items(),
            key=lambda item: item[0].value,
        ):
            lines.append(
                f"{vote.value}: {count}"
            )

        lines.append("")
        lines.append("Committee Members")

        for member, count in sorted(
            member_counts.items(),
            key=lambda item: item[0].value,
        ):
            lines.append(
                f"{member.value}: {count}"
            )

        return "\n".join(lines)
