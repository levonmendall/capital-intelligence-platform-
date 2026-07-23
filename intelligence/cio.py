"""Chief Investment Officer orchestration."""

from __future__ import annotations

from abc import ABC, abstractmethod

from committee.meeting import CommitteeMeeting
from intelligence.cio_guidance import CIOGuidance


class GuidanceSynthesizer(ABC):
    """Interface for committee-to-guidance synthesis."""

    @abstractmethod
    def synthesize(
        self,
        meeting: CommitteeMeeting,
    ) -> CIOGuidance:
        """Convert a committee meeting into official CIO guidance."""

        raise NotImplementedError


class ChiefInvestmentOfficer:
    """Issues official guidance based on a committee meeting."""

    def __init__(self, synthesizer: GuidanceSynthesizer) -> None:
        self.synthesizer = synthesizer

    def issue_guidance(
        self,
        meeting: CommitteeMeeting,
    ) -> CIOGuidance:
        """Issue official CIO guidance."""

        return self.synthesizer.synthesize(meeting)
