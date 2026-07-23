from committee.consensus import CommitteeConsensus
from committee.meeting import InvestmentCommittee
from committee.member import CommitteeMember
from committee.opinion import CommitteeOpinion
from intelligence.briefing import CIOBriefing


class MockEconomist(CommitteeMember):
    name = "Chief Economist"
    specialty = "Macroeconomics"

    def evaluate(
        self,
        briefing: CIOBriefing,
    ) -> CommitteeOpinion:
        return CommitteeOpinion(
            member=self.name,
            specialty=self.specialty,
            outlook="Growth is slowing",
            confidence=0.75,
            recommendation="Maintain moderate caution",
            evidence=["Leading indicators are weakening"],
            risks=["Credit conditions may tighten"],
            opportunities=["Inflation may continue declining"],
        )


class MockRiskOfficer(CommitteeMember):
    name = "Risk Officer"
    specialty = "Portfolio Risk"

    def evaluate(
        self,
        briefing: CIOBriefing,
    ) -> CommitteeOpinion:
        return CommitteeOpinion(
            member=self.name,
            specialty=self.specialty,
            outlook="Downside risk is elevated",
            confidence=0.80,
            recommendation="Retain additional liquidity",
            evidence=["Valuations remain elevated"],
            risks=["Potential drawdown"],
        )


def test_committee_collects_one_opinion_per_member() -> None:
    committee = InvestmentCommittee(
        members=[
            MockEconomist(),
            MockRiskOfficer(),
        ]
    )

    briefing = CIOBriefing(
        macro={"growth_trend": "slowing"},
        valuation={"equity_valuation": "elevated"},
    )

    opinions = committee.collect_opinions(briefing)

    assert len(opinions) == 2
    assert opinions[0].member == "Chief Economist"
    assert opinions[1].member == "Risk Officer"


def test_committee_conducts_meeting() -> None:
    committee = InvestmentCommittee(
        members=[
            MockEconomist(),
            MockRiskOfficer(),
        ]
    )

    briefing = CIOBriefing(
        macro={"growth_trend": "slowing"},
    )

    consensus = CommitteeConsensus(
        majority_view="Slower but positive growth",
        confidence=0.72,
        agreements=[
            "Growth momentum is weakening",
            "Liquidity should remain available",
        ],
        disagreements=[
            "Magnitude of recession risk",
        ],
    )

    meeting = committee.conduct_meeting(
        briefing=briefing,
        consensus=consensus,
        meeting_summary=(
            "The committee expects slower growth and recommends "
            "moderate caution."
        ),
    )

    assert len(meeting.opinions) == 2
    assert meeting.consensus.majority_view == (
        "Slower but positive growth"
    )
    assert meeting.briefing is briefing
