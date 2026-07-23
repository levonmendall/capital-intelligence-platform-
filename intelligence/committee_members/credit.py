"""Credit Committee member for investment-governance review."""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import InvestmentRecommendation


class CreditCommitteeMember(CommitteeMember):
    """
    Specialist committee responsible for evaluating credit quality,
    balance-sheet durability, and financial resilience.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.CREDIT

    @property
    def display_name(self) -> str:
        return "Credit Committee"

    @property
    def voting_weight(self) -> float:
        return 1.0

    @property
    def has_veto(self) -> bool:
        return True

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
            self._financial_strength_adjustment(recommendation),
            self._balance_sheet_adjustment(recommendation),
            self._cash_flow_adjustment(recommendation),
            self._credit_disclosure_adjustment(recommendation),
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
    def _financial_strength_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        evidence = len(recommendation.supporting_evidence)

        if evidence >= 4:
            value = 0.04
        elif evidence >= 2:
            value = 0.02
        elif evidence >= 1:
            value = 0.00
        else:
            value = -0.05

        return ScoreAdjustment(
            category=AdjustmentCategory.CREDIT,
            description="Assessment of overall financial strength.",
            raw_value=value,
        )

    @staticmethod
    def _balance_sheet_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.risks:
            value = 0.01
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.CREDIT,
            description="Assessment of balance-sheet resilience.",
            raw_value=value,
        )

    @staticmethod
    def _cash_flow_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.invalidation_conditions:
            value = 0.02
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.CREDIT,
            description="Assessment of cash-flow durability.",
            raw_value=value,
        )

    @staticmethod
    def _credit_disclosure_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if (
            recommendation.supporting_evidence
            and recommendation.contradicting_evidence
        ):
            value = 0.03
        elif recommendation.supporting_evidence:
            value = -0.01
        else:
            value = -0.05

        return ScoreAdjustment(
            category=AdjustmentCategory.POLICY,
            description="Assessment of financial disclosure quality.",
            raw_value=value,
        )

    @staticmethod
    def _build_rationale(
        recommendation: InvestmentRecommendation,
    ) -> str:

        return (
            f"The Credit Committee evaluated the financial durability "
            f"of {recommendation.target}, considering financial "
            "strength, balance-sheet quality, cash-flow resilience, "
            "and disclosure quality."
        )

    @staticmethod
    def _build_strengths(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        strengths = []

        if recommendation.supporting_evidence:
            strengths.append(
                "Financial evidence supports the recommendation."
            )

        if recommendation.invalidation_conditions:
            strengths.append(
                "Financial deterioration can be monitored through "
                "defined invalidation conditions."
            )

        if not strengths:
            strengths.append(
                "The recommendation can be evaluated under the "
                "credit-governance framework."
            )

        return tuple(strengths)

    @staticmethod
    def _build_concerns(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        concerns = []

        if not recommendation.supporting_evidence:
            concerns.append(
                "Financial evidence supporting the recommendation "
                "is limited."
            )

        if not recommendation.risks:
            concerns.append(
                "Financial risks have not been documented."
            )

        if not recommendation.contradicting_evidence:
            concerns.append(
                "Contradictory financial evidence is absent."
            )

        return tuple(concerns)

    @staticmethod
    def _build_suggested_changes(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        changes = []

        if not recommendation.supporting_evidence:
            changes.append(
                "Provide additional financial evidence."
            )

        if not recommendation.risks:
            changes.append(
                "Document material financial risks."
            )

        if not recommendation.invalidation_conditions:
            changes.append(
                "Define measurable financial failure conditions."
            )

        if not recommendation.contradicting_evidence:
            changes.append(
                "Address contradictory financial evidence."
            )

        return tuple(changes)
