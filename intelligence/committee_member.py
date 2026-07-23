"""
Abstract base class for all investment committee members.

Committee members are responsible only for performing
discipline-specific analysis.

Voting, confidence normalization, and opinion construction are
handled centrally by the DecisionFramework.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_framework import (
    DecisionFramework,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class CommitteeMember(ABC):
    """
    Base class for all investment committee members.

    Every committee member follows the same workflow:

        Recommendation
              ↓
        assess()
              ↓
        CommitteeAssessment
              ↓
        DecisionFramework
              ↓
        CommitteeOpinion

    Subclasses implement only their analytical logic.
    """

    def __init__(
        self,
        framework: DecisionFramework | None = None,
    ) -> None:

        self._framework = (
            framework
            if framework is not None
            else DecisionFramework()
        )

    @property
    def framework(self) -> DecisionFramework:
        """
        Shared decision framework.
        """

        return self._framework

    @property
    @abstractmethod
    def role(self) -> CommitteeRole:
        """
        Committee specialization.
        """

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable committee member name.
        """

    @property
    def voting_weight(self) -> float:
        """
        Relative voting influence.

        Override for weighted committees.
        """

        return 1.0

    @property
    def has_veto(self) -> bool:
        """
        Whether this committee member possesses veto authority.

        Defaults to False.
        """

        return False

    @abstractmethod
    def assess(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeAssessment:
        """
        Perform discipline-specific analysis.

        Returns
        -------
        CommitteeAssessment
        """

    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeOpinion:
        """
        Execute the complete evaluation workflow.

        This method should almost never be overridden.
        """

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an InvestmentRecommendation."
            )

        assessment = self.assess(
            recommendation
        )

        return self.framework.build_opinion(
            recommendation_identifier=
                recommendation.identifier,

            member=self,

            assessment=assessment,
        )

    def supports(
        self,
        recommendation: InvestmentRecommendation,
    ) -> bool:
        """
        Returns True when the member approves or strongly approves
        the recommendation.
        """

        opinion = self.evaluate(
            recommendation
        )

        return opinion.vote.value in {
            "approve",
            "strongly_approve",
        }

    def objects(
        self,
        recommendation: InvestmentRecommendation,
    ) -> bool:
        """
        Returns True when the member objects to the recommendation.
        """

        opinion = self.evaluate(
            recommendation
        )

        return opinion.vote.value in {
            "object",
            "strongly_object",
        }

    def confidence(
        self,
        recommendation: InvestmentRecommendation,
    ) -> float:
        """
        Convenience accessor for the final normalized confidence.
        """

        return self.evaluate(
            recommendation
        ).confidence

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(role={self.role.value!r}, "
            f"name={self.display_name!r}, "
            f"weight={self.voting_weight})"
        )
