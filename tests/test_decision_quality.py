"""Tests for process-versus-outcome decision evaluation."""

from datetime import datetime, timezone

import pytest

from evaluation import (
    DecisionOutcome,
    DecisionQualityClassification,
    DecisionQualityReview,
    ProcessVerdict,
)


NOW = datetime(2025, 5, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("process", "outcome", "expected"),
    [
        (
            ProcessVerdict.DISCIPLINED,
            DecisionOutcome.POSITIVE,
            DecisionQualityClassification.DISCIPLINED_POSITIVE,
        ),
        (
            ProcessVerdict.DISCIPLINED,
            DecisionOutcome.NEGATIVE,
            DecisionQualityClassification.DISCIPLINED_NEGATIVE,
        ),
        (
            ProcessVerdict.FLAWED,
            DecisionOutcome.POSITIVE,
            DecisionQualityClassification.FLAWED_POSITIVE,
        ),
        (
            ProcessVerdict.FLAWED,
            DecisionOutcome.NEGATIVE,
            DecisionQualityClassification.FLAWED_NEGATIVE,
        ),
        (
            ProcessVerdict.UNRESOLVED,
            DecisionOutcome.UNRESOLVED,
            DecisionQualityClassification.INCONCLUSIVE,
        ),
    ],
)
def test_decision_quality_does_not_conflate_luck_and_process(
    process: ProcessVerdict,
    outcome: DecisionOutcome,
    expected: DecisionQualityClassification,
) -> None:
    review = DecisionQualityReview(
        decision_identifier="decision-1",
        reviewed_at=NOW,
        process_verdict=process,
        outcome=outcome,
        process_evidence=("Policy review completed.",),
        outcome_evidence=("Benchmark-relative return measured.",),
        lessons=(),
        reviewer="CIO",
    )

    assert review.classification is expected
