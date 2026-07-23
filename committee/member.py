"""Abstract investment committee member."""

from __future__ import annotations

from abc import ABC, abstractmethod

from committee.opinion import CommitteeOpinion
from intelligence.briefing import CIOBriefing


class CommitteeMember(ABC):
    """Interface implemented by every investment committee specialist."""

    name: str
    specialty: str

    @abstractmethod
    def evaluate(self, briefing: CIOBriefing) -> CommitteeOpinion:
        """Evaluate a briefing and return a structured opinion."""

        raise NotImplementedError
