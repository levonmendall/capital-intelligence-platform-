"""Base class for all investment committee members."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.committee_opinion import (
    CommitteeOpinion,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class CommitteeMember(ABC):
    """
    Abstract investment committee member.

    Every committee member evaluates a recommendation from a
    specific discipline.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name."""

    @abstractmethod
    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> CommitteeOpinion:
        """
        Produce one committee opinion.
        """
