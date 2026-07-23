"""Tests for committee adjustment domain models."""

import pytest

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    AdjustmentSet,
    ScoreAdjustment,
)


def test_score_adjustment_defaults_applied_to_raw() -> None:
    adjustment = ScoreAdjustment(
        category=AdjustmentCategory.ECONOMIC,
        description="Positive economic alignment.",
        raw_value=0.08,
    )

    assert adjustment.raw_value == 0.08
    assert adjustment.applied_value == 0.08
    assert adjustment.value == 0.08
    assert adjustment.was_constrained is False


def test_score_adjustment_preserves_constraint() -> None:
    adjustment = ScoreAdjustment(
        category=AdjustmentCategory.POLICY,
        description="Policy-limited adjustment.",
        raw_value=0.25,
        applied_value=0.20,
        constraint_reason="Policy cap.",
    )

    assert adjustment.was_constrained is True
    assert adjustment.constraint_reason == "Policy cap."


def test_score_adjustment_rejects_empty_description() -> None:
    with pytest.raises(ValueError):
        ScoreAdjustment(
            category=AdjustmentCategory.RISK,
            description=" ",
            raw_value=-0.05,
        )


@pytest.mark.parametrize(
    "value",
    [-1.01, 1.01],
)
def test_score_adjustment_rejects_invalid_values(
    value: float,
) -> None:
    with pytest.raises(ValueError):
        ScoreAdjustment(
            category=AdjustmentCategory.OTHER,
            description="Invalid adjustment.",
            raw_value=value,
        )


def test_adjustment_set_aggregates_values() -> None:
    adjustments = AdjustmentSet(
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.ECONOMIC,
                description="Economic support.",
                raw_value=0.08,
            ),
            ScoreAdjustment(
                category=AdjustmentCategory.RISK,
                description="Risk concern.",
                raw_value=-0.03,
            ),
        )
    )

    assert adjustments.total_raw_adjustment == 0.05
    assert adjustments.total_applied_adjustment == 0.05
    assert len(adjustments.positives) == 1
    assert len(adjustments.negatives) == 1


def test_adjustment_set_filters_by_category() -> None:
    economic = ScoreAdjustment(
        category=AdjustmentCategory.ECONOMIC,
        description="Economic support.",
        raw_value=0.05,
    )

    risk = ScoreAdjustment(
        category=AdjustmentCategory.RISK,
        description="Risk concern.",
        raw_value=-0.02,
    )

    adjustments = AdjustmentSet(
        adjustments=(economic, risk)
    )

    assert adjustments.by_category(
        AdjustmentCategory.ECONOMIC
    ) == (economic,)


def test_adjustment_set_rejects_invalid_member() -> None:
    with pytest.raises(TypeError):
        AdjustmentSet(
            adjustments=("invalid",)  # type: ignore[arg-type]
        )
