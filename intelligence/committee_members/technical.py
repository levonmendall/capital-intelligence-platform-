"""Technical Committee member for investment-governance review."""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import InvestmentRecommendation


class TechnicalCommitteeMember(CommitteeMember):
    """
    Specialist committee responsible for evaluating technical
    confirmation, trend quality, momentum, volatility, and timing risk.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.TECHNICAL

    @property
    def display_name(self) -> str:
        return "Technical Committee"

    @property
    def voting_weight(self) -> float:
        return 1.0

    @property
    def has_veto(self) -> bool:
        return False

    def assess(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeAssessment:

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an InvestmentRecommendation"
            )

        adjustments = (
            self._trend_adjustment(recommendation),
            self._momentum_adjustment(recommendation),
            self._volatility_adjustment(recommendation),
            self._timing_adjustment(recommendation),
        )

        return self.build_assessment(
            recommendation=recommendation,
            adjustments=adjustments,
            rationale=self._build_rationale(recommendation),
            strengths=self._build_strengths(recommendation),
            concerns=self._build_concerns(recommendation),
            suggested_changes=self._build_suggested_changes(
                recommendation
            ),
        )

    @staticmethod
    def _trend_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        evidence = len(recommendation.supporting_evidence)

        value = (
            0.04 if evidence >= 4 else
            0.02 if evidence >= 2 else
            0.00 if evidence >= 1 else
            -0.05
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.TECHNICAL,
            description="Assessment of trend confirmation.",
            raw_value=value,
        )

    @staticmethod
    def _momentum_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        value = (
            0.02 if recommendation.supporting_evidence
            else -0.03
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.TECHNICAL,
            description="Assessment of momentum quality.",
            raw_value=value,
        )

    @staticmethod
    def _volatility_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        value = (
            0.02 if recommendation.risks
            else -0.03
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.RISK,
            description="Assessment of volatility risk.",
            raw_value=value,
        )

    @staticmethod
    def _timing_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        value = (
            0.02 if recommendation.invalidation_conditions
            else -0.03
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.ALLOCATION,
            description="Assessment of entry and exit timing.",
            raw_value=value,
        )

    @staticmethod
    def _build_rationale(
        recommendation: InvestmentRecommendation,
    ) -> str:

        return (
            f"The Technical Committee evaluated "
            f"{recommendation.target} for trend, momentum, "
            "volatility, and timing confirmation."
        )

    @staticmethod
    def _build_strengths(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        strengths = []

        if recommendation.supporting_evidence:
            strengths.append(
                "Technical evidence supports the recommendation."
            )

        if recommendation.invalidation_conditions:
            strengths.append(
                "Exit timing has been defined."
            )

        if not strengths:
            strengths.append(
                "The recommendation can be evaluated under the technical framework."
            )

        return tuple(strengths)

    @staticmethod
    def _build_concerns(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        concerns = []

        if not recommendation.supporting_evidence:
            concerns.append(
                "Technical confirmation is limited."
            )

        if not recommendation.risks:
            concerns.append(
                "Volatility risks are not documented."
            )

        if not recommendation.invalidation_conditions:
            concerns.append(
                "Timing criteria are not defined."
            )

        return tuple(concerns)

    @staticmethod
    def _build_suggested_changes(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        changes = []

        if not recommendation.supporting_evidence:
            changes.append(
                "Provide additional technical confirmation."
            )

        if not recommendation.risks:
            changes.append(
                "Document volatility risks."
            )

        if not recommendation.invalidation_conditions:
            changes.append(
                "Define technical exit criteria."
            )

        return tuple(changes)
