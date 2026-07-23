"""
Abstract base class for all investment committee members.

Committee members perform discipline-specific analysis. The
AdjustmentEngine applies scoring policy, and the DecisionFramework
converts the completed assessment into a CommitteeOpinion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from intelligence.committee_adjustment import (
    ScoreAdjustment,
)
from intelligence.committee_adjustment_engine import (
    AdjustmentEngine,
)
from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_framework import (
    DecisionFramework,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
    CommitteeVote,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class CommitteeMember(ABC):
    """
    Base class for investment committee participants.

    Shared workflow:

        InvestmentRecommendation
                  ↓
             assess()
                  ↓
          ScoreAdjustments
                  ↓
          AdjustmentEngine
                  ↓
        CommitteeAssessment
                  ↓
        DecisionFramework
                  ↓
         CommitteeOpinion
    """

    def __init__(
        self,
        framework: DecisionFramework | None = None,
        adjustment_engine: AdjustmentEngine | None = None,
    ) -> None:
        self._framework = (
            framework
            if framework is not None
            else DecisionFramework()
        )

        self._adjustment_engine = (
            adjustment_engine
            if adjustment_engine is not None
            else AdjustmentEngine()
        )

    @property
    def framework(self) -> DecisionFramework:
        """Shared voting framework."""

        return self._framework

    @property
    def adjustment_engine(self) -> AdjustmentEngine:
        """Shared adjustment engine."""

        return self._adjustment_engine

    @property
    @abstractmethod
    def role(self) -> CommitteeRole:
        """Committee specialization."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable committee participant name."""

    @property
    def voting_weight(self) -> float:
        """Relative voting influence."""

        return 1.0

    @property
    def has_veto(self) -> bool:
        """Whether this member possesses veto authority."""

        return False

    @abstractmethod
    def assess(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeAssessment:
        """Perform discipline-specific analysis."""

    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeOpinion:
        """Execute the complete standardized workflow."""

        self._validate_recommendation(
            recommendation
        )

        assessment = self.assess(
            recommendation
        )

        if not isinstance(
            assessment,
            CommitteeAssessment,
        ):
            raise TypeError(
                "assess() must return a CommitteeAssessment."
            )

        return self.framework.build_opinion(
            recommendation_identifier=
                recommendation.identifier,
            member=self,
            assessment=assessment,
        )

    def build_assessment(
        self,
        *,
        recommendation: InvestmentRecommendation,
        adjustments: tuple[ScoreAdjustment, ...],
        rationale: str,
        strengths: tuple[str, ...] = (),
        concerns: tuple[str, ...] = (),
        suggested_changes: tuple[str, ...] = (),
    ) -> CommitteeAssessment:
        """
        Build an assessment using the shared AdjustmentEngine.

        Concrete committee members should call this method instead
        of manually aggregating confidence adjustments.
        """

        self._validate_recommendation(
            recommendation
        )

        outcome = self.adjustment_engine.apply(
            base_confidence=recommendation.confidence,
            adjustments=adjustments,
        )

        return CommitteeAssessment(
            base_confidence=
                outcome.base_confidence,
            adjusted_confidence=
                outcome.adjusted_confidence,
            adjustments=outcome.adjustments,
            rationale=rationale,
            strengths=strengths,
            concerns=concerns,
            suggested_changes=suggested_changes,
        )

    def supports(
        self,
        recommendation: InvestmentRecommendation,
    ) -> bool:
        """Whether the member approves the recommendation."""

        return self.evaluate(
            recommendation
        ).vote in {
            CommitteeVote.APPROVE,
            CommitteeVote.STRONGLY_APPROVE,
        }

    def objects(
        self,
        recommendation: InvestmentRecommendation,
    ) -> bool:
        """Whether the member objects to the recommendation."""

        return self.evaluate(
            recommendation
        ).vote in {
            CommitteeVote.OBJECT,
            CommitteeVote.STRONGLY_OBJECT,
        }

    def confidence(
        self,
        recommendation: InvestmentRecommendation,
    ) -> float:
        """Return normalized final confidence."""

        return self.evaluate(
            recommendation
        ).confidence

    @staticmethod
    def _validate_recommendation(
        recommendation: InvestmentRecommendation,
    ) -> None:
        """Validate committee input."""

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an "
                "InvestmentRecommendation."
            )

    def __repr__(self) -> str:
        """Developer-friendly representation."""

        return (
            f"{self.__class__.__name__}"
            f"(role={self.role.value!r}, "
            f"name={self.display_name!r}, "
            f"weight={self.voting_weight}, "
            f"veto={self.has_veto})"
        )
