"""
Macro Committee Member.

Evaluates recommendations from a top-down macroeconomic perspective.

The Macro Committee considers:

- Economic regime alignment
- Recommendation confidence
- Time horizon
- Asset allocation level
- Overall macro conviction

It intentionally does NOT consider valuation,
credit quality, liquidity, or technicals.
"""

from __future__ import annotations

from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import (
    InvestmentRecommendation,
    RecommendationLevel,
)


class MacroCommitteeMember(CommitteeMember):
    """
    Committee member specializing in macroeconomic analysis.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.MACRO

    @property
    def display_name(self) -> str:
        return "Macro Committee"

    def assess(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeAssessment:

        confidence = recommendation.confidence

        confidence += self._allocation_bonus(
            recommendation
        )

        confidence += self._duration_bonus(
            recommendation
        )

        confidence = self.framework.clamp(
            confidence
        )

        strengths = self._strengths(
            recommendation
        )

        concerns = self._concerns(
            recommendation
        )

        suggested_changes = self._changes(
            recommendation
        )

        rationale = self._rationale(
            recommendation,
            confidence,
        )

        return CommitteeAssessment(
            adjusted_confidence=confidence,
            rationale=rationale,
            strengths=tuple(strengths),
            concerns=tuple(concerns),
            suggested_changes=tuple(
                suggested_changes
            ),
        )

    def _allocation_bonus(
        self,
        recommendation: InvestmentRecommendation,
    ) -> float:
        """
        Macro committee places greater confidence in
        higher-level allocation decisions.
        """

        bonuses = {
            RecommendationLevel.MACRO: 0.08,
            RecommendationLevel.ASSET_CLASS: 0.06,
            RecommendationLevel.SECTOR: 0.03,
            RecommendationLevel.INDUSTRY: 0.01,
            RecommendationLevel.SECURITY: 0.00,
        }

        return bonuses.get(
            recommendation.level,
            0.0,
        )

    def _duration_bonus(
        self,
        recommendation: InvestmentRecommendation,
    ) -> float:
        """
        Macro themes generally have more confidence over
        intermediate and longer horizons.
        """

        months = recommendation.expected_duration_months

        if months >= 24:
            return 0.05

        if months >= 12:
            return 0.03

        if months >= 6:
            return 0.01

        return -0.02

    def _strengths(
        self,
        recommendation: InvestmentRecommendation,
    ) -> list[str]:

        strengths = [
            "Recommendation aligns with top-down macro allocation."
        ]

        if recommendation.expected_duration_months >= 12:
            strengths.append(
                "Investment horizon is appropriate for macro positioning."
            )

        if recommendation.confidence >= 0.80:
            strengths.append(
                "Underlying research exhibits strong conviction."
            )

        return strengths

    def _concerns(
        self,
        recommendation: InvestmentRecommendation,
    ) -> list[str]:

        concerns = []

        if recommendation.expected_duration_months < 6:
            concerns.append(
                "Macro themes often require longer investment horizons."
            )

        if recommendation.confidence < 0.60:
            concerns.append(
                "Underlying recommendation confidence is limited."
            )

        return concerns

    def _changes(
        self,
        recommendation: InvestmentRecommendation,
    ) -> list[str]:

        changes = []

        if recommendation.expected_duration_months < 6:
            changes.append(
                "Consider extending the expected investment horizon."
            )

        return changes

    @staticmethod
    def _rationale(
        recommendation: InvestmentRecommendation,
        confidence: float,
    ) -> str:

        return (
            "Macro Committee evaluated the recommendation from a "
            "top-down economic perspective. "
            f"Adjusted confidence is {confidence:.2%}."
        )
