"""Tests for transparent investment recommendation rules."""

import pytest

from intelligence.recommendation import (
    ExpectedReturn,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
)
from intelligence.recommendation_rules import (
    RecommendationRules,
)
from intelligence.theme import ThemeCategory
from intelligence.thesis import (
    InvestmentThesis,
    ThesisDirection,
    ThesisHorizon,
    ThesisStatus,
)


def build_thesis(
    *,
    identifier: str = (
        "long-duration-quality-in-disinflation"
    ),
    title: str = (
        "Long-Duration Quality Benefits From Disinflation"
    ),
    direction: ThesisDirection = ThesisDirection.BULLISH,
    status: ThesisStatus = ThesisStatus.ACTIVE,
    confidence: float = 0.82,
    beneficiaries: tuple[str, ...] = (
        "quality_growth_equities",
        "investment_grade_bonds",
    ),
) -> InvestmentThesis:
    return InvestmentThesis(
        identifier=identifier,
        title=title,
        source_theme_identifier=(
            "disinflation-with-positive-growth"
        ),
        source_theme_category=ThemeCategory.INFLATION,
        direction=direction,
        horizon=ThesisHorizon.CYCLICAL,
        status=status,
        confidence=confidence,
        proposition=(
            "The thesis supports differentiated asset performance."
        ),
        supporting_evidence=(
            "Inflation is moderating.",
            "Growth remains positive.",
        ),
        contradicting_evidence=(
            "Policy may remain restrictive.",
        ),
        beneficiaries=beneficiaries,
        losers=(
            "weak_balance_sheet_assets",
        ),
        catalysts=(
            "Further inflation moderation",
        ),
        risks=(
            "Inflation reacceleration",
        ),
        increase_conviction_conditions=(
            "Inflation continues improving",
        ),
        reduce_conviction_conditions=(
            "Inflation progress stalls",
        ),
        invalidation_conditions=(
            "Inflation and growth deteriorate together",
        ),
        expected_duration_months=12,
    )


def test_disinflation_thesis_generates_two_recommendations() -> None:
    recommendations = RecommendationRules().apply(
        build_thesis()
    )

    assert len(recommendations) == 2

    identifiers = {
        recommendation.identifier
        for recommendation in recommendations
    }

    assert (
        "overweight-investment-grade-bonds-"
        "during-disinflation"
        in identifiers
    )

    assert (
        "accumulate-quality-growth-equities-"
        "during-disinflation"
        in identifiers
    )


def test_credit_quality_thesis_generates_credit_actions() -> None:
    thesis = build_thesis(
        identifier="higher-quality-credit-outperforms",
        title=(
            "Higher-Quality Credit Outperforms "
            "Lower-Quality Borrowers"
        ),
        direction=ThesisDirection.SELECTIVE,
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert len(recommendations) == 2

    by_target = {
        recommendation.target: recommendation
        for recommendation in recommendations
    }

    assert (
        by_target["investment_grade_credit"].action
        == RecommendationAction.OVERWEIGHT
    )

    assert (
        by_target["lower_quality_credit"].action
        == RecommendationAction.UNDERWEIGHT
    )


def test_cyclical_thesis_generates_asset_and_sector_levels() -> None:
    thesis = build_thesis(
        identifier=(
            "cyclical-assets-benefit-from-reacceleration"
        ),
        title=(
            "Cyclical Assets Benefit From "
            "Economic Reacceleration"
        ),
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    levels = {
        recommendation.level
        for recommendation in recommendations
    }

    assert RecommendationLevel.ASSET_CLASS in levels
    assert RecommendationLevel.SECTOR in levels


def test_manufacturing_weakness_generates_sector_underweight() -> None:
    thesis = build_thesis(
        identifier=(
            "industrial-cyclicals-face-near-term-headwinds"
        ),
        title=(
            "Industrial Cyclicals Face Near-Term Headwinds"
        ),
        direction=ThesisDirection.BEARISH,
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.target == "industrials"
    assert (
        recommendation.level
        == RecommendationLevel.SECTOR
    )
    assert (
        recommendation.action
        == RecommendationAction.UNDERWEIGHT
    )
    assert (
        recommendation.magnitude
        == RecommendationMagnitude.SMALL
    )


def test_recession_hedge_rule_generates_macro_recommendation() -> None:
    thesis = build_thesis(
        identifier="maintain-downside-hedges",
        title=(
            "Maintain Downside Protection "
            "Against Recession Risk"
        ),
        direction=ThesisDirection.SELECTIVE,
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    recommendation = recommendations[0]

    assert (
        recommendation.level
        == RecommendationLevel.MACRO
    )
    assert recommendation.target == "recession_protection"
    assert (
        recommendation.action
        == RecommendationAction.ACCUMULATE
    )


def test_unknown_bullish_thesis_uses_generic_overweight_rule() -> None:
    thesis = build_thesis(
        identifier="unknown-bullish-thesis",
        title="Unknown Bullish Thesis",
        direction=ThesisDirection.BULLISH,
        beneficiaries=("emerging_asset_class",),
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.identifier == (
        "unknown-bullish-thesis-generic-recommendation"
    )
    assert recommendation.target == "emerging_asset_class"
    assert (
        recommendation.action
        == RecommendationAction.OVERWEIGHT
    )
    assert recommendation.expected_return == ExpectedReturn.HIGH
    assert recommendation.confidence == 0.72


def test_unknown_bearish_thesis_uses_generic_underweight_rule() -> None:
    thesis = build_thesis(
        identifier="unknown-bearish-thesis",
        title="Unknown Bearish Thesis",
        direction=ThesisDirection.BEARISH,
        beneficiaries=("vulnerable_asset",),
    )

    recommendation = RecommendationRules().apply(
        thesis
    )[0]

    assert (
        recommendation.action
        == RecommendationAction.UNDERWEIGHT
    )
    assert recommendation.expected_return == ExpectedReturn.LOW


def test_invalidated_thesis_generates_no_recommendations() -> None:
    thesis = build_thesis(
        status=ThesisStatus.INVALIDATED,
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert recommendations == ()


def test_rule_preserves_source_thesis_identifier() -> None:
    thesis = build_thesis()

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert all(
        recommendation.source_thesis_identifier
        == thesis.identifier
        for recommendation in recommendations
    )


def test_rule_preserves_thesis_evidence_and_risks() -> None:
    thesis = build_thesis()

    recommendation = RecommendationRules().apply(
        thesis
    )[0]

    assert (
        recommendation.supporting_evidence
        == thesis.supporting_evidence
    )
    assert (
        recommendation.contradicting_evidence
        == thesis.contradicting_evidence
    )
    assert recommendation.catalysts == thesis.catalysts
    assert recommendation.risks == thesis.risks
    assert (
        recommendation.invalidation_conditions
        == thesis.invalidation_conditions
    )


def test_confidence_adjustment_is_clamped_by_builder() -> None:
    thesis = build_thesis(
        confidence=1.0,
    )

    recommendations = RecommendationRules().apply(
        thesis
    )

    assert all(
        0.0 <= recommendation.confidence <= 1.0
        for recommendation in recommendations
    )


def test_rules_reject_wrong_input_type() -> None:
    with pytest.raises(TypeError):
        RecommendationRules().apply(
            "not a thesis"  # type: ignore[arg-type]
        )
