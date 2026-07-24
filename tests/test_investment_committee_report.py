from datetime import datetime, timezone

from intelligence.investment_committee import (
    InvestmentCommittee,
)
from intelligence.investment_committee_report import (
    InvestmentCommitteeReport,
)
from intelligence.investment_committee_report_generator import (
    InvestmentCommitteeReportGenerator,
)
from intelligence.investment_committee_result import (
    InvestmentCommitteeResult,
)
from intelligence.committee_statistics import (
    CommitteeStatisticsCalculator,
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


def make_recommendation() -> InvestmentRecommendation:
    return InvestmentRecommendation(
        identifier="rec-report-1",
        title="Report test recommendation",
        level=RecommendationLevel.SECURITY,
        target="TEST",
        action=RecommendationAction.ACCUMULATE,
        magnitude=RecommendationMagnitude.MODERATE,
        status=RecommendationStatus.ACTIVE,
        confidence=0.80,
        source_thesis_identifier="thesis-report-1",
        rationale=(
            "A sufficiently detailed rationale."
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


def test_generator_builds_canonical_report() -> None:
    generated_at = datetime(
        2026,
        7,
        23,
        12,
        0,
        tzinfo=timezone.utc,
    )

    decision = InvestmentCommittee().evaluate(
        make_recommendation()
    )

    report = InvestmentCommitteeReportGenerator(
        clock=lambda: generated_at,
        identifier_factory=lambda: "icr-test-1",
    ).generate(decision)

    assert isinstance(
        report,
        InvestmentCommitteeReport,
    )
    assert report.report_identifier == "icr-test-1"
    assert report.generated_at == generated_at
    assert report.decision == decision
    assert (
        report.recommendation_identifier
        == "rec-report-1"
    )
    assert (
        report.committee_count
        == decision.opinion_count
    )
    assert (
        report.supportive_count
        + report.neutral_count
        + report.opposed_count
        == report.committee_count
    )
    assert report.strengths == decision.strengths
    assert report.concerns == decision.concerns
    assert (
        report.required_changes
        == decision.required_changes
    )
    assert (
        "Report test recommendation"
        in report.executive_summary
    )


def test_generator_is_deterministic_with_injected_dependencies() -> None:
    generated_at = datetime(
        2026,
        7,
        23,
        12,
        0,
        tzinfo=timezone.utc,
    )

    decision = InvestmentCommittee().evaluate(
        make_recommendation()
    )

    generator = InvestmentCommitteeReportGenerator(
        clock=lambda: generated_at,
        identifier_factory=lambda: "icr-test-1",
    )

    assert (
        generator.generate(decision)
        == generator.generate(decision)
    )


def test_committee_result_bundles_consistent_artifacts() -> None:
    generated_at = datetime(
        2026,
        7,
        23,
        12,
        0,
        tzinfo=timezone.utc,
    )
    decision = InvestmentCommittee().evaluate(
        make_recommendation()
    )
    report = InvestmentCommitteeReportGenerator(
        clock=lambda: generated_at,
        identifier_factory=lambda: "icr-result-test",
    ).generate(decision)
    statistics = CommitteeStatisticsCalculator().calculate(
        decision
    )

    result = InvestmentCommitteeResult(
        decision=decision,
        report=report,
        statistics=statistics,
        generated_at=generated_at,
    )

    assert result.decision == decision
    assert result.report == report
    assert result.statistics == statistics
    assert result.generated_at == generated_at
