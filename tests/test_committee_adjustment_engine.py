"""Tests for the committee adjustment engine."""

import pytest

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_adjustment_engine import (
    AdjustmentEngine,
    AdjustmentPolicy,
)


def test_engine_applies_adjustments() -> None:
    engine = AdjustmentEngine()

    outcome = engine.apply(
        base_confidence=0.70,
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.ECONOMIC,
                description="Economic support.",
                raw_value=0.08,
            ),
            ScoreAdjustment(
                category=AdjustmentCategory.DURATION,
                description="Long horizon.",
                raw_value=0.05,
            ),
        ),
    )

    assert outcome.base_confidence == 0.70
    assert outcome.adjusted_confidence == 0.83
    assert (
        outcome.adjustments
        .total_applied_adjustment
        == 0.13
    )


def test_engine_limits_single_adjustment() -> None:
    engine = AdjustmentEngine(
        AdjustmentPolicy(
            maximum_single_adjustment=0.10,
            maximum_positive_adjustment=0.30,
            maximum_negative_adjustment=0.30,
        )
    )

    outcome = engine.apply(
        base_confidence=0.50,
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.ECONOMIC,
                description="Oversized support.",
                raw_value=0.25,
            ),
        ),
    )

    adjustment = outcome.adjustments[0]

    assert adjustment.raw_value == 0.25
    assert adjustment.applied_value == 0.10
    assert adjustment.was_constrained is True
    assert outcome.adjusted_confidence == 0.60


def test_engine_limits_cumulative_positive_adjustments() -> None:
    engine = AdjustmentEngine(
        AdjustmentPolicy(
            maximum_single_adjustment=0.20,
            maximum_positive_adjustment=0.15,
            maximum_negative_adjustment=0.30,
        )
    )

    outcome = engine.apply(
        base_confidence=0.50,
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.ECONOMIC,
                description="First support.",
                raw_value=0.10,
            ),
            ScoreAdjustment(
                category=AdjustmentCategory.ALLOCATION,
                description="Second support.",
                raw_value=0.10,
            ),
        ),
    )

    assert outcome.adjustments[0].applied_value == 0.10
    assert outcome.adjustments[1].applied_value == 0.05
    assert outcome.adjusted_confidence == 0.65


def test_engine_limits_cumulative_negative_adjustments() -> None:
    engine = AdjustmentEngine(
        AdjustmentPolicy(
            maximum_single_adjustment=0.20,
            maximum_positive_adjustment=0.30,
            maximum_negative_adjustment=0.15,
        )
    )

    outcome = engine.apply(
        base_confidence=0.70,
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.RISK,
                description="First concern.",
                raw_value=-0.10,
            ),
            ScoreAdjustment(
                category=AdjustmentCategory.LIQUIDITY,
                description="Second concern.",
                raw_value=-0.10,
            ),
        ),
    )

    assert outcome.adjustments[0].applied_value == -0.10
    assert outcome.adjustments[1].applied_value == -0.05
    assert outcome.adjusted_confidence == 0.55


def test_engine_clamps_final_confidence() -> None:
    engine = AdjustmentEngine(
        AdjustmentPolicy(
            maximum_single_adjustment=1.0,
            maximum_positive_adjustment=1.0,
            maximum_negative_adjustment=1.0,
        )
    )

    outcome = engine.apply(
        base_confidence=0.95,
        adjustments=(
            ScoreAdjustment(
                category=AdjustmentCategory.ECONOMIC,
                description="Strong support.",
                raw_value=0.25,
            ),
        ),
    )

    assert outcome.adjusted_confidence == 1.0


def test_engine_rejects_invalid_adjustment_collection() -> None:
    engine = AdjustmentEngine()

    with pytest.raises(TypeError):
        engine.apply(
            base_confidence=0.50,
            adjustments=["invalid"],  # type: ignore[arg-type]
        )
