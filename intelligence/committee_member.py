"""Abstract investment committee participant."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class CommitteeMember(ABC):
    """
    Base class for every investment committee participant.

    Committee members are independent experts that evaluate
    recommendations from their own discipline.
    """

    @property
    @abstractmethod
    def role(self) -> CommitteeRole:
        """Committee specialization."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable committee member name."""

    @property
    def voting_weight(self) -> float:
        """
        Relative influence of this member.

        Default:
            1.0

        The InvestmentCommittee can later assign larger weights
        to the CIO or Risk Committee without modifying subclasses.
        """

        return 1.0

    @property
    def has_veto(self) -> bool:
        """
        Whether this committee member can veto a proposal.

        Defaults to False.
        """

        return False

    @abstractmethod
    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeOpinion:
        """
        Produce an independent opinion regarding one recommendation.
        """
