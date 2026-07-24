"""Architecture tests for canonical committee ownership and workflow."""

from datetime import datetime, timezone

from committee.recommendation_governance import (
    RecommendationCommitteeConsensus,
    RecommendationCommitteeDecision,
    RecommendationCommitteePolicy,
    RecommendationInvestmentCommittee,
)
from committee.workflow import InstitutionalDecisionWorkflow
from intelligence.investment_committee import InvestmentCommittee
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.investment_policy import InvestmentPolicy
from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationStatus,
)


def make_recommendation() -> InvestmentRecommendation:
    return InvestmentRecommendation(
        identifier="rec-architecture-1",
        title="Architecture workflow recommendation",
        level=RecommendationLevel.ASSET_CLASS,
        target="Investment Grade Bonds",
        action=RecommendationAction.OVERWEIGHT,
        magnitude=RecommendationMagnitude.MODERATE,
        status=RecommendationStatus.ACTIVE,
        confidence=0.80,
        source_thesis_identifier="thesis-architecture-1",
        rationale="Disinflation supports high-quality duration.",
        supporting_evidence=("Inflation momentum is moderating.",),
        contradicting_evidence=("Growth remains resilient.",),
        catalysts=("Policy becomes less restrictive.",),
        risks=("Inflation reaccelerates.",),
        invalidation_conditions=("Core inflation accelerates.",),
        expected_return=ExpectedReturn.MODERATE,
        expected_risk=ExpectedRisk.LOW,
        expected_duration_months=18,
    )


def test_canonical_governance_paths_preserve_class_identity() -> None:
    assert RecommendationInvestmentCommittee is InvestmentCommittee
    assert RecommendationCommitteeConsensus is InvestmentCommitteeConsensus
    assert RecommendationCommitteeDecision is InvestmentCommitteeDecision
    assert RecommendationCommitteePolicy is InvestmentPolicy


def test_workflow_produces_one_consistent_result_bundle() -> None:
    result = InstitutionalDecisionWorkflow().evaluate(
        make_recommendation()
    )

    assert result.report.decision is result.decision
    assert result.generated_at == result.report.generated_at
    assert result.generated_at.tzinfo is not None
    assert (
        result.statistics.committee_size
        == result.decision.opinion_count
    )
    assert result.report.recommendation_identifier == (
        result.decision.recommendation.identifier
    )


def test_workflow_rejects_non_recommendations() -> None:
    workflow = InstitutionalDecisionWorkflow()

    try:
        workflow.evaluate("not a recommendation")
    except TypeError as error:
        assert "InvestmentRecommendation" in str(error)
    else:
        raise AssertionError("workflow accepted an invalid recommendation")


def test_workflow_uses_timezone_aware_timestamp() -> None:
    result = InstitutionalDecisionWorkflow().evaluate(
        make_recommendation()
    )

    assert isinstance(result.generated_at, datetime)
    assert result.generated_at.utcoffset() == timezone.utc.utcoffset(
        result.generated_at
    )
