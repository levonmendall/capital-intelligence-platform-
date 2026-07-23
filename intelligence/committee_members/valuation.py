"""Valuation Committee member for investment-governance review."""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import InvestmentRecommendation


class ValuationCommitteeMember(CommitteeMember):
    """
    Specialist committee responsible for evaluating valuation quality,
    margin of safety, and pricing discipline.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.VALUATION

    @property
    def display_name(self) -> str:
        return "Valuation Committee"

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
            self._valuation_support_adjustment(
                recommendation
            ),
            self._margin_of_safety_adjustment(
                recommendation
            ),
            self._pricing_discipline_adjustment(
                recommendation
            ),
            self._valuation_disclosure_adjustment(
                recommendation
            ),
        )

        return self.build_assessment(
            recommendation=recommendation,
            adjustments=adjustments,
            rationale=self._build_rationale(
                recommendation
            ),
            strengths=self._build_strengths(
                recommendation
            ),
            concerns=self._build_concerns(
                recommendation
            ),
            suggested_changes=self._build_suggested_changes(
                recommendation
            ),
        )

    @staticmethod
    def _valuation_support_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        evidence = len(
            recommendation.supporting_evidence
        )

        if evidence >= 4:
            value = 0.05
        elif evidence >= 2:
            value = 0.03
        elif evidence >= 1:
            value = 0.00
        else:
            value = -0.05

        return ScoreAdjustment(
            category=AdjustmentCategory.VALUATION,
            description="Assessment of valuation support.",
            raw_value=value,
        )

    @staticmethod
    def _margin_of_safety_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.contradicting_evidence:
            value = 0.02
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.VALUATION,
            description="Assessment of margin of safety.",
            raw_value=value,
        )

    @staticmethod
    def _pricing_discipline_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.invalidation_conditions:
            value = 0.02
        else:
            value = -0.02

        return ScoreAdjustment(
            category=AdjustmentCategory.ALLOCATION,
            description="Assessment of valuation discipline.",
            raw_value=value,
        )

    @staticmethod
    def _valuation_disclosure_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.risks:
            value = 0.02
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.POLICY,
            description="Assessment of valuation disclosure.",
            raw_value=value,
        )

    @staticmethod
    def _build_rationale(
        recommendation: InvestmentRecommendation,
    ) -> str:

        return (
            f"The Valuation Committee evaluated "
            f"{recommendation.target} for valuation "
            "support, pricing discipline, margin of "
            "safety, and valuation transparency."
        )

    @staticmethod
    def _build_strengths(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        strengths = []

        if recommendation.supporting_evidence:
            strengths.append(
                "The recommendation includes valuation support."
            )

        if recommendation.contradicting_evidence:
            strengths.append(
                "Alternative valuation viewpoints are acknowledged."
            )

        if recommendation.invalidation_conditions:
            strengths.append(
                "Valuation assumptions are measurable."
            )

        if not strengths:
            strengths.append(
                "The recommendation can be evaluated under the valuation framework."
            )

        return tuple(strengths)

    @staticmethod
    def _build_concerns(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        concerns = []

        if not recommendation.supporting_evidence:
            concerns.append(
                "Valuation support is limited."
            )

        if not recommendation.contradicting_evidence:
            concerns.append(
                "Alternative valuation scenarios are not discussed."
            )

        if not recommendation.risks:
            concerns.append(
                "Valuation risks are not documented."
            )

        return tuple(concerns)

    @staticmethod
    def _build_suggested_changes(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        changes = []

        if not recommendation.supporting_evidence:
            changes.append(
                "Provide additional valuation evidence."
            )

        if not recommendation.contradicting_evidence:
            changes.append(
                "Document competing valuation scenarios."
            )

        if not recommendation.invalidation_conditions:
            changes.append(
                "Define valuation invalidation criteria."
            )

        if not recommendation.risks:
            changes.append(
                "Document valuation-specific risks."
            )

        return tuple(changes)
