"""Risk Committee member for investment-governance review."""

from __future__ import annotations

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_member import CommitteeMember
from intelligence.committee_opinion import CommitteeRole
from intelligence.recommendation import InvestmentRecommendation


class RiskCommitteeMember(CommitteeMember):
    """
    Specialist committee member responsible for downside-risk review.

    The Risk Committee evaluates:

    - the recommendation's inherent expected risk
    - the quality of identified risks and invalidation conditions
    - the proposed recommendation magnitude
    - the balance between supporting and contradicting evidence

    It produces raw score adjustments. Policy enforcement and final
    confidence calculation remain centralized in AdjustmentEngine.
    """

    @property
    def role(self) -> CommitteeRole:
        return CommitteeRole.RISK

    @property
    def display_name(self) -> str:
        return "Risk Committee"

    @property
    def voting_weight(self) -> float:
        return 1.25

    @property
    def has_veto(self) -> bool:
        return True

    def assess(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeAssessment:
        """Assess an investment recommendation from a risk perspective."""

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an InvestmentRecommendation"
            )

        adjustments = (
            self._expected_risk_adjustment(recommendation),
            self._downside_control_adjustment(recommendation),
            self._magnitude_adjustment(recommendation),
            self._evidence_balance_adjustment(recommendation),
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
    def _normalized_enum_name(value: object) -> str:
        """
        Return a normalized name for an enum-like value.

        This permits the Risk Committee to support the repository's
        existing enums without coupling the implementation to every
        possible enum member.
        """

        name = getattr(value, "name", None)

        if isinstance(name, str):
            return name.strip().upper()

        raw_value = getattr(value, "value", value)

        return str(raw_value).strip().upper().replace(" ", "_")

    @classmethod
    def _expected_risk_adjustment(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """Score the recommendation's stated expected-risk level."""

        risk_name = cls._normalized_enum_name(
            recommendation.expected_risk
        )

        scores = {
            "VERY_LOW": 0.04,
            "LOW": 0.03,
            "MODERATE": 0.00,
            "MEDIUM": 0.00,
            "HIGH": -0.05,
            "VERY_HIGH": -0.09,
            "EXTREME": -0.12,
        }

        raw_value = scores.get(risk_name, -0.02)

        descriptions = {
            "VERY_LOW": (
                "The recommendation carries very low stated risk."
            ),
            "LOW": (
                "The recommendation carries a comparatively low "
                "stated risk level."
            ),
            "MODERATE": (
                "The recommendation carries a moderate and manageable "
                "stated risk level."
            ),
            "MEDIUM": (
                "The recommendation carries a moderate and manageable "
                "stated risk level."
            ),
            "HIGH": (
                "The recommendation carries a high stated risk level."
            ),
            "VERY_HIGH": (
                "The recommendation carries a very high stated "
                "risk level."
            ),
            "EXTREME": (
                "The recommendation carries an extreme stated "
                "risk level."
            ),
        }

        description = descriptions.get(
            risk_name,
            (
                "The recommendation's expected-risk classification "
                "is not recognized by the current risk framework."
            ),
        )

        return ScoreAdjustment(
            category=AdjustmentCategory.RISK,
            description=description,
            raw_value=raw_value,
        )

    @staticmethod
    def _downside_control_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """
        Score the quality of documented risks and invalidation controls.

        Strong recommendations should identify both what can go wrong
        and what conditions would invalidate the investment thesis.
        """

        risk_count = len(recommendation.risks)
        invalidation_count = len(
            recommendation.invalidation_conditions
        )

        if risk_count >= 2 and invalidation_count >= 1:
            raw_value = 0.04
            description = (
                "The recommendation documents multiple material risks "
                "and explicit invalidation conditions."
            )
        elif risk_count >= 1 and invalidation_count >= 1:
            raw_value = 0.02
            description = (
                "The recommendation identifies downside risk and an "
                "explicit invalidation condition."
            )
        elif risk_count >= 1:
            raw_value = -0.02
            description = (
                "The recommendation identifies risk but does not define "
                "a clear invalidation condition."
            )
        elif invalidation_count >= 1:
            raw_value = -0.03
            description = (
                "The recommendation defines invalidation conditions "
                "without sufficiently documenting underlying risks."
            )
        else:
            raw_value = -0.08
            description = (
                "The recommendation does not document material risks "
                "or explicit invalidation conditions."
            )

        return ScoreAdjustment(
            category=AdjustmentCategory.POLICY,
            description=description,
            raw_value=raw_value,
        )

    @classmethod
    def _magnitude_adjustment(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """
        Score whether the proposed recommendation magnitude increases
        portfolio risk.
        """

        magnitude_name = cls._normalized_enum_name(
            recommendation.magnitude
        )

        scores = {
            "MINIMAL": 0.03,
            "SMALL": 0.02,
            "MODEST": 0.01,
            "MODERATE": 0.00,
            "MEDIUM": 0.00,
            "LARGE": -0.04,
            "SIGNIFICANT": -0.05,
            "AGGRESSIVE": -0.08,
            "MAXIMUM": -0.10,
        }

        raw_value = scores.get(magnitude_name, -0.01)

        if raw_value > 0:
            description = (
                "The proposed recommendation magnitude limits "
                "portfolio-level downside exposure."
            )
        elif raw_value == 0:
            description = (
                "The proposed recommendation magnitude is moderate "
                "and does not require an additional risk adjustment."
            )
        else:
            description = (
                "The proposed recommendation magnitude increases "
                "portfolio-level downside exposure."
            )

        return ScoreAdjustment(
            category=AdjustmentCategory.ALLOCATION,
            description=description,
            raw_value=raw_value,
        )

    @staticmethod
    def _evidence_balance_adjustment(
        recommendation: InvestmentRecommendation,
    ) -> ScoreAdjustment:
        """
        Score whether the recommendation acknowledges uncertainty.

        A recommendation with supporting evidence and credible
        contradicting evidence is generally more risk-aware than one
        presenting only a one-sided case.
        """

        supporting_count = len(
            recommendation.supporting_evidence
        )
        contradicting_count = len(
            recommendation.contradicting_evidence
        )

        if supporting_count >= 2 and contradicting_count >= 1:
            raw_value = 0.03
            description = (
                "The recommendation presents substantial supporting "
                "evidence while acknowledging contradictory evidence."
            )
        elif supporting_count >= 1 and contradicting_count >= 1:
            raw_value = 0.01
            description = (
                "The recommendation presents both supporting and "
                "contradictory evidence."
            )
        elif supporting_count >= 2:
            raw_value = -0.02
            description = (
                "The recommendation has supporting evidence but does "
                "not adequately acknowledge contradictory evidence."
            )
        elif supporting_count >= 1:
            raw_value = -0.04
            description = (
                "The recommendation has limited supporting evidence "
                "and does not adequately address contrary evidence."
            )
        else:
            raw_value = -0.08
            description = (
                "The recommendation lacks sufficient evidence for "
                "a reliable downside-risk assessment."
            )

        return ScoreAdjustment(
            category=AdjustmentCategory.RISK,
            description=description,
            raw_value=raw_value,
        )

    @classmethod
    def _build_rationale(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> str:
        risk_name = cls._normalized_enum_name(
            recommendation.expected_risk
        ).replace("_", " ").lower()

        magnitude_name = cls._normalized_enum_name(
            recommendation.magnitude
        ).replace("_", " ").lower()

        return (
            f"The Risk Committee evaluated {recommendation.target} "
            f"as a {magnitude_name} recommendation with {risk_name} "
            "expected risk. The review considered inherent downside, "
            "position magnitude, invalidation discipline, and the "
            "balance of supporting and contradictory evidence."
        )

    @classmethod
    def _build_strengths(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        strengths: list[str] = []

        risk_name = cls._normalized_enum_name(
            recommendation.expected_risk
        )

        magnitude_name = cls._normalized_enum_name(
            recommendation.magnitude
        )

        if risk_name in {
            "VERY_LOW",
            "LOW",
            "MODERATE",
            "MEDIUM",
        }:
            strengths.append(
                "The stated expected-risk level is within the "
                "committee's normal tolerance range."
            )

        if (
            len(recommendation.risks) >= 2
            and len(
                recommendation.invalidation_conditions
            )
            >= 1
        ):
            strengths.append(
                "Material downside risks and explicit invalidation "
                "conditions are documented."
            )

        if magnitude_name in {
            "MINIMAL",
            "SMALL",
            "MODEST",
            "MODERATE",
            "MEDIUM",
        }:
            strengths.append(
                "The proposed recommendation magnitude limits "
                "concentration and drawdown exposure."
            )

        if (
            len(recommendation.supporting_evidence) >= 1
            and len(
                recommendation.contradicting_evidence
            )
            >= 1
        ):
            strengths.append(
                "The evidence set acknowledges both the investment "
                "case and material counterarguments."
            )

        if not strengths:
            strengths.append(
                "The recommendation can be evaluated within the "
                "current risk-governance framework."
            )

        return tuple(strengths)

    @classmethod
    def _build_concerns(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        concerns: list[str] = []

        risk_name = cls._normalized_enum_name(
            recommendation.expected_risk
        )

        magnitude_name = cls._normalized_enum_name(
            recommendation.magnitude
        )

        if risk_name in {
            "HIGH",
            "VERY_HIGH",
            "EXTREME",
        }:
            concerns.append(
                "The stated expected-risk level may exceed normal "
                "portfolio tolerance."
            )

        if not recommendation.risks:
            concerns.append(
                "Material downside risks have not been documented."
            )

        if not recommendation.invalidation_conditions:
            concerns.append(
                "The recommendation lacks an explicit condition for "
                "invalidating the investment thesis."
            )

        if magnitude_name in {
            "LARGE",
            "SIGNIFICANT",
            "AGGRESSIVE",
            "MAXIMUM",
        }:
            concerns.append(
                "The proposed magnitude may create excessive "
                "concentration or drawdown exposure."
            )

        if not recommendation.contradicting_evidence:
            concerns.append(
                "The recommendation does not sufficiently acknowledge "
                "contradictory evidence."
            )

        if len(recommendation.supporting_evidence) == 0:
            concerns.append(
                "The recommendation lacks sufficient supporting "
                "evidence for risk approval."
            )

        return tuple(concerns)

    @classmethod
    def _build_suggested_changes(
        cls,
        recommendation: InvestmentRecommendation,
    ) -> tuple[str, ...]:
        changes: list[str] = []

        risk_name = cls._normalized_enum_name(
            recommendation.expected_risk
        )

        magnitude_name = cls._normalized_enum_name(
            recommendation.magnitude
        )

        if risk_name in {
            "HIGH",
            "VERY_HIGH",
            "EXTREME",
        }:
            changes.append(
                "Reduce the recommendation's expected downside or "
                "provide explicit portfolio hedging."
            )

        if not recommendation.risks:
            changes.append(
                "Document the principal downside risks before approval."
            )

        if not recommendation.invalidation_conditions:
            changes.append(
                "Define measurable thesis-invalidation conditions."
            )

        if magnitude_name in {
            "LARGE",
            "SIGNIFICANT",
            "AGGRESSIVE",
            "MAXIMUM",
        }:
            changes.append(
                "Reduce the proposed magnitude or introduce staged "
                "position sizing."
            )

        if not recommendation.contradicting_evidence:
            changes.append(
                "Add credible contradictory evidence and explain why "
                "the recommendation remains justified."
            )

        if not recommendation.supporting_evidence:
            changes.append(
                "Develop additional supporting evidence before "
                "risk approval."
            )

        return tuple(changes)
