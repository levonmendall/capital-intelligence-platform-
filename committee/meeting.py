"""Investment committee meeting orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field

from committee.consensus import CommitteeConsensus
from committee.member import CommitteeMember
from committee.opinion import CommitteeOpinion
from intelligence.briefing import CIOBriefing
from intelligence.metadata import DocumentMetadata


@dataclass
class CommitteeMeeting:
    """Permanent record of an investment committee meeting."""

    briefing: CIOBriefing
    opinions: list[CommitteeOpinion]
    consensus: CommitteeConsensus
    meeting_summary: str

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def __post_init__(self) -> None:
        if not self.opinions:
            raise ValueError(
                "CommitteeMeeting requires at least one committee opinion"
            )


class InvestmentCommittee:
    """Conducts committee meetings using registered specialist members."""

    def __init__(self, members: list[CommitteeMember]) -> None:
        if not members:
            raise ValueError(
                "InvestmentCommittee requires at least one member"
            )

        self.members = members

    def collect_opinions(
        self,
        briefing: CIOBriefing,
    ) -> list[CommitteeOpinion]:
        """Ask every committee member to evaluate the same briefing."""

        return [member.evaluate(briefing) for member in self.members]

    def conduct_meeting(
        self,
        briefing: CIOBriefing,
        consensus: CommitteeConsensus,
        meeting_summary: str,
    ) -> CommitteeMeeting:
        """Conduct and record an investment committee meeting."""

        opinions = self.collect_opinions(briefing)

        return CommitteeMeeting(
            briefing=briefing,
            opinions=opinions,
            consensus=consensus,
            meeting_summary=meeting_summary,
        )
