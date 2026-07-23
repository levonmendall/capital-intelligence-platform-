from intelligence.committee_opinion import (
    CommitteeRole,
)
from intelligence.investment_committee import (
    InvestmentCommittee,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationStatus,
)


def make_recommendation(
    confidence: float = 0.80,
) -> InvestmentRecommendation:
    return InvestmentRecommendation(
        identifier="rec-1",
        title="Test recommendation",
        level=RecommendationLevel.SECURITY,
        target="TEST",
        action=RecommendationAction.ACCUMULATE,
        magnitude=RecommendationMagnitude.MODERATE,
        status=RecommendationStatus.ACTIVE,
        confidence=confidence,
        source_thesis_identifier="thesis-1",
        rationale=(
            "A sufficiently detailed investment rationale."
        ),
        supporting_evidence=(
            "Evidence one",
            "Evidence two",
        ),
        contradicting_evidence=(
            "Counter evidence",
        ),
        catalysts=(
            "Catalyst",
        ),
        risks=(
            "Risk one",
            "Risk two",
        ),
        invalidation_conditions=(
            "Invalidation condition",
        ),
        expected_return=ExpectedReturn.HIGH,
        expected_risk=ExpectedRisk.MODERATE,
        expected_duration_months=12,
    )


def test_default_committee_evaluates_all_roles() -> None:
    decision = InvestmentCommittee().evaluate(
        make_recommendation()
    )

    assert isinstance(
        decision,
        InvestmentCommitteeDecision,
    )

    assert decision.opinion_count == 6

    assert {
        opinion.member
        for opinion in decision.opinions
    } == set(CommitteeRole)

    assert isinstance(
        decision.consensus,
        InvestmentCommitteeConsensus,
    )

    assert 0.0 <= decision.confidence <= 1.0


def test_evaluation_is_deterministic() -> None:
    committee = InvestmentCommittee()
    recommendation = make_recommendation()

    first = committee.evaluate(
        recommendation
    )

    second = committee.evaluate(
        recommendation
    )

    assert first == second
