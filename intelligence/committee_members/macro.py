"""
Macro Committee Member.

Evaluates investment recommendations from a top-down macroeconomic
perspective.

The Macro Committee considers:

- recommendation level
- investment horizon
- underlying research confidence
- suitability for macro allocation

It intentionally does not perform dedicated valuation, credit,
liquidity, technical, or portfolio-risk analysis.
"""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_member import (
    CommitteeMember,
)
from intelligence.committee_opinion import (
    CommitteeRole,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
    RecommendationLevel,
)


class MacroCommitteeMember(CommitteeMember):
    """
    Committee participant specializing in macroeconomic analysis.
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
        """Perform macro-specific recommendation analysis."""

        adjustments = (
            self._allocation_adjustment(
                recommendation
            ),
            self._duration_adjustment(
                recommendation
            ),
            self._research_confidence_adjustment(
                recommendation
            ),
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
            recommendation
        )

        return self.build_assessment(
            recommendation=recommendation,
            adjustments=adjustments,
            rationale=rationale,
            strengths=strengths,
            concerns=concerns,
            suggested_changes=
                suggested_changes,
        )

    @staticmethod
    def _allocation_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """Score recommendation-level macro relevance."""

        values = {
            RecommendationLevel.MACRO: 0.08,
            RecommendationLevel.ASSET_CLASS: 0.06,
            RecommendationLevel.SECTOR: 0.03,
            RecommendationLevel.INDUSTRY: 0.01,
            RecommendationLevel.SECURITY: 0.00,
        }

        value = values.get(
            recommendation.level,
            0.0,
        )

        descriptions = {
            RecommendationLevel.MACRO:
                "Recommendation directly expresses a macro view.",
            RecommendationLevel.ASSET_CLASS:
                "Asset-class positioning is strongly influenced "
                "by the macro regime.",
            RecommendationLevel.SECTOR:
                "Sector positioning has meaningful macro sensitivity.",
            RecommendationLevel.INDUSTRY:
                "Industry positioning has limited direct macro scope.",
            RecommendationLevel.SECURITY:
                "Security selection receives no macro-level bonus.",
        }

        description = descriptions.get(
            recommendation.level,
            "Recommendation level provides no macro adjustment.",
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.ALLOCATION,
            description=description,
            raw_value=value,
        )

    @staticmethod
    def _duration_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """Score the suitability of the investment horizon."""

        months = (
            recommendation.expected_duration_months
        )

        if months >= 24:
            value = 0.05
            description = (
                "Long investment horizon supports macro positioning."
            )

        elif months >= 12:
            value = 0.03
            description = (
                "Intermediate horizon is suitable for macro themes."
            )

        elif months >= 6:
            value = 0.01
            description = (
                "Investment horizon provides limited time "
                "for the macro thesis to develop."
            )

        else:
            value = -0.02
            description = (
                "Short investment horizon may not allow the "
                "macro thesis to develop."
            )

        return ScoreAdjustment(
            category=AdjustmentCategory.DURATION,
            description=description,
            raw_value=value,
        )

    @staticmethod
    def _research_confidence_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """Score the quality of underlying research conviction."""

        if recommendation.confidence >= 0.85:
            value = 0.03
            description = (
                "Underlying research demonstrates very high conviction."
            )

        elif recommendation.confidence >= 0.75:
            value = 0.01
            description = (
                "Underlying research demonstrates strong conviction."
            )

        elif recommendation.confidence < 0.55:
            value = -0.05
            description = (
                "Underlying research confidence is insufficient "
                "for strong macro conviction."
            )

        elif recommendation.confidence < 0.65:
            value = -0.02
            description = (
                "Underlying research confidence is below the "
                "preferred macro threshold."
            )

        else:
            value = 0.00
            description = (
                "Underlying research confidence provides no "
                "additional macro adjustment."
            )

        return ScoreAdjustment(
            category=AdjustmentCategory.ECONOMIC,
            description=description,
            raw_value=value,
        )

    @staticmethod
    def _strengths(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        """Identify macro strengths."""

        strengths: list[str] = []

        if recommendation.level in {
            RecommendationLevel.MACRO,
            RecommendationLevel.ASSET_CLASS,
        }:
            strengths.append(
                "Recommendation is expressed at a level "
                "appropriate for macro allocation."
            )

        if (
            recommendation.expected_duration_months
            >= 12
        ):
            strengths.append(
                "Investment horizon is appropriate for "
                "macro positioning."
            )

        if recommendation.confidence >= 0.75:
            strengths.append(
                "Underlying research exhibits strong conviction."
            )

        if not strengths:
            strengths.append(
                "Recommendation can be evaluated within the "
                "current macro framework."
            )

        return tuple(strengths)

    @staticmethod
    def _concerns(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        """Identify macro concerns."""

        concerns: list[str] = []

        if (
            recommendation.expected_duration_months
            < 6
        ):
            concerns.append(
                "Macro themes often require a longer "
                "investment horizon."
            )

        if recommendation.confidence < 0.60:
            concerns.append(
                "Underlying recommendation confidence is limited."
            )

        if (
            recommendation.level
            == RecommendationLevel.SECURITY
        ):
            concerns.append(
                "Security-specific outcomes may be driven by "
                "factors outside the macro thesis."
            )

        return tuple(concerns)

    @staticmethod
    def _changes(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        """Recommend macro-related revisions."""

        changes: list[str] = []

        if (
            recommendation.expected_duration_months
            < 6
        ):
            changes.append(
                "Consider extending the expected investment horizon."
            )

        if (
            recommendation.level
            == RecommendationLevel.SECURITY
        ):
            changes.append(
                "Pair the security recommendation with an explicit "
                "asset-class or sector allocation view."
            )

        if recommendation.confidence < 0.60:
            changes.append(
                "Develop additional macro evidence before approval."
            )

        return tuple(changes)

    @staticmethod
    def _rationale(
        recommendation: InvestmentRecommendation,
    ) -> str:
        """Construct the macro assessment rationale."""

        return (
            "The Macro Committee evaluated "
            f"{recommendation.target!r} from a top-down "
            "economic and asset-allocation perspective. "
            "Confidence was adjusted for recommendation level, "
            "investment horizon, and underlying research conviction."
        )
