"""Liquidity Committee member for investment-governance review."""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import InvestmentRecommendation


class LiquidityCommitteeMember(CommitteeMember):
    """
    Specialist committee responsible for evaluating liquidity,
    execution quality, and exit risk.

    The Liquidity Committee evaluates:

    - expected market liquidity
    - execution risk
    - position sizing
    - exit flexibility

    It produces score adjustments while leaving policy enforcement
    and confidence calculation to the AdjustmentEngine.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.LIQUIDITY

    @property
    def display_name(self) -> str:
        return "Liquidity Committee"

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
            self._market_liquidity_adjustment(
                recommendation
            ),
            self._execution_adjustment(
                recommendation
            ),
            self._position_size_adjustment(
                recommendation
            ),
            self._exit_strategy_adjustment(
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
    def _market_liquidity_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        evidence = len(
            recommendation.supporting_evidence
        )

        if evidence >= 4:
            value = 0.04
        elif evidence >= 2:
            value = 0.02
        elif evidence >= 1:
            value = 0.00
        else:
            value = -0.05

        return ScoreAdjustment(
            category=AdjustmentCategory.LIQUIDITY,
            description=(
                "Assessment of expected market liquidity."
            ),
            raw_value=value,
        )

    @staticmethod
    def _execution_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.risks:
            value = 0.02
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.LIQUIDITY,
            description=(
                "Assessment of execution risk."
            ),
            raw_value=value,
        )

    @staticmethod
    def _position_size_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:

        if recommendation.invalidation_conditions:
            value = 0.02
        else:
            value = -0.03

        return ScoreAdjustment(
            category=AdjustmentCategory.ALLOCATION,
            description=(
                "Assessment of position sizing."
            ),
            raw_value=value,
        )

    @staticmethod
    def _exit_strategy_adjustment(
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
            description=(
                "Assessment of exit strategy quality."
            ),
            raw_value=value,
        )

    @staticmethod
    def _build_rationale(
        recommendation: InvestmentRecommendation,
    ) -> str:

        return (
            f"The Liquidity Committee evaluated "
            f"{recommendation.target} for market "
            "liquidity, execution quality, position "
            "sizing, and exit flexibility."
        )

    @staticmethod
    def _build_strengths(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        strengths = []

        if recommendation.supporting_evidence:
            strengths.append(
                "Evidence supports acceptable liquidity."
            )

        if recommendation.invalidation_conditions:
            strengths.append(
                "Exit conditions are documented."
            )

        if not strengths:
            strengths.append(
                "The recommendation can be evaluated "
                "within the liquidity-governance "
                "framework."
            )

        return tuple(strengths)

    @staticmethod
    def _build_concerns(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        concerns = []

        if not recommendation.risks:
            concerns.append(
                "Liquidity risks have not been documented."
            )

        if not recommendation.invalidation_conditions:
            concerns.append(
                "Exit conditions are not defined."
            )

        if not recommendation.contradicting_evidence:
            concerns.append(
                "Contradictory liquidity evidence is "
                "absent."
            )

        return tuple(concerns)

    @staticmethod
    def _build_suggested_changes(
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:

        changes = []

        if not recommendation.risks:
            changes.append(
                "Document liquidity-specific risks."
            )

        if not recommendation.invalidation_conditions:
            changes.append(
                "Define measurable exit conditions."
            )

        if not recommendation.contradicting_evidence:
            changes.append(
                "Address adverse liquidity scenarios."
            )

        if not recommendation.supporting_evidence:
            changes.append(
                "Provide additional liquidity evidence."
            )

        return tuple(changes)
