"""Integration tests for governance package boundaries."""

from committee.opinion import (
    CommitteeOpinion as MeetingCommitteeOpinion,
)
from intelligence.committee_opinion import (
    CommitteeOpinion as IntelligenceCommitteeOpinion,
    CommitteeOpinionSet,
    CommitteeRole,
    CommitteeVote,
)


def test_committee_layers_use_distinct_opinion_models() -> None:
    """
    The committee package owns meeting-oriented opinions.

    The intelligence package owns analytical specialist opinions.
    Their models intentionally serve different responsibilities.
    """

    assert MeetingCommitteeOpinion is not IntelligenceCommitteeOpinion


def test_intelligence_opinion_model_is_available() -> None:
    opinion = IntelligenceCommitteeOpinion(
        recommendation_identifier="REC-001",
        member=CommitteeRole.RISK,
        vote=CommitteeVote.OBJECT,
        confidence=0.40,
        rationale="Downside exposure requires further controls.",
        strengths=(),
        concerns=("Expected drawdown is elevated.",),
        suggested_changes=("Reduce the proposed allocation.",),
    )

    assert opinion.recommendation_identifier == "REC-001"
    assert opinion.member == CommitteeRole.RISK
    assert opinion.vote == CommitteeVote.OBJECT
    assert opinion.confidence == 0.40


def test_intelligence_opinion_set_accepts_specialist_opinions() -> None:
    opinion = IntelligenceCommitteeOpinion(
        recommendation_identifier="REC-002",
        member=CommitteeRole.MACRO,
        vote=CommitteeVote.APPROVE,
        confidence=0.80,
        rationale="The macro regime supports the recommendation.",
    )

    opinions = CommitteeOpinionSet(
        opinions=(opinion,)
    )

    assert len(opinions) == 1
    assert opinions[0] is opinion
    assert opinions.recommendation_identifier == "REC-002"
