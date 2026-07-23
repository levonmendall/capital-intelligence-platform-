"""Tests for the investment recommendation engine."""

from __future__ import annotations

import pytest

from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationSet,
    RecommendationStatus,
)
from intelligence.recommendation_engine import (
    RecommendationEngine,
)
from intelligence.theme import ThemeCategory
from intelligence.thesis import (
    InvestmentThesis,
    InvestmentThesisSet,
    ThesisDirection,
    ThesisHorizon,
    ThesisStatus,
)


def build_thesis(
    *,
    identifier: str,
    title: str,
    direction: ThesisDirection = ThesisDirection.BULLISH,
    status: ThesisStatus = ThesisStatus.ACTIVE,
    confidence: float = 0.82,
) -> InvestmentThesis:
    return InvestmentThesis(
        identifier=identifier,
        title=title,
        source_theme_identifier="test-theme",
        source_theme_category=ThemeCategory.GROWTH,
        direction=direction,
        horizon=ThesisHorizon.CYCLICAL,
        status=status,
        confidence=confidence,
        proposition="The thesis supports differentiated performance.",
        supporting_evidence=(
            f"Evidence supporting {identifier}",
        ),
        contradicting_evidence=(
            f"Evidence contradicting {identifier}",
        ),
        beneficiaries=(
            "quality_assets",
        ),
        losers=(
            "lower_quality_assets",
        ),
        catalysts=(
            f"Catalyst for {identifier}",
        ),
        risks=(
            f"Risk for {identifier}",
        ),
        increase_conviction_conditions=(
            "Supporting conditions improve",
        ),
        reduce_conviction_conditions=(
            "Supporting conditions weaken",
        ),
        invalidation_conditions=(
            f"Invalidation for {identifier}",
        ),
        expected_duration_months=12,
    )


def build_thesis_set(
    *theses: InvestmentThesis,
) -> InvestmentThesisSet:
    return InvestmentThesisSet(
        theses=tuple(theses),
        confidence=0.80,
        summary="Test thesis set",
    )


def build_recommendation(
    *,
    identifier: str,
    source_thesis_identifier: str,
    confidence: float,
    magnitude: RecommendationMagnitude,
    supporting_evidence: tuple[str, ...],
    target: str = "investment_grade_credit",
    action: RecommendationAction = (
        RecommendationAction.OVERWEIGHT
    ),
    level: RecommendationLevel = (
        RecommendationLevel.ASSET_CLASS
    ),
) -> InvestmentRecommendation:
    return InvestmentRecommendation(
        identifier=identifier,
        title="Overweight Investment-Grade Credit",
        level=level,
        target=target,
        action=action,
        magnitude=magnitude,
        status=RecommendationStatus.ACTIVE,
        confidence=confidence,
        source_thesis_identifier=source_thesis_identifier,
        rationale=(
            f"Rationale from {source_thesis_identifier}."
        ),
        supporting_evidence=supporting_evidence,
        contradicting_evidence=(
            f"Contradiction from {source_thesis_identifier}",
        ),
        catalysts=(
            f"Catalyst from {source_thesis_identifier}",
        ),
        risks=(
            f"Risk from {source_thesis_identifier}",
        ),
        invalidation_conditions=(
            f"Invalidation from {source_thesis_identifier}",
        ),
        expected_return=ExpectedReturn.MODERATE,
        expected_risk=ExpectedRisk.LOW,
        expected_duration_months=12,
    )


class StubRules:
    """Deterministic test double for RecommendationRules."""

    def __init__(
        self,
        recommendations_by_thesis: dict[
            str,
            tuple[InvestmentRecommendation, ...],
        ],
    ) -> None:
        self._recommendations_by_thesis = (
            recommendations_by_thesis
        )

    def apply(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return self._recommendations_by_thesis.get(
            thesis.identifier,
            (),
        )


def test_generate_returns_recommendation_set() -> None:
    thesis = build_thesis(
        identifier="higher-quality-credit-outperforms",
        title="Higher-Quality Credit Outperforms",
    )

    result = RecommendationEngine().generate(
        build_thesis_set(thesis)
    )

    assert isinstance(result, RecommendationSet)
    assert result.recommendations
    assert 0.0 <= result.confidence <= 1.0
    assert result.summary.startswith(
        "Recommendation Summary"
    )


def test_generate_rejects_invalid_input_type() -> None:
    with pytest.raises(
        TypeError,
        match="InvestmentThesisSet",
    ):
        RecommendationEngine().generate(
            "not a thesis set"  # type: ignore[arg-type]
        )


def test_generate_raises_when_no_recommendations_exist() -> None:
    invalidated = build_thesis(
        identifier="invalidated-thesis",
        title="Invalidated Thesis",
        status=ThesisStatus.INVALIDATED,
    )

    with pytest.raises(
        ValueError,
        match="No recommendations",
    ):
        RecommendationEngine().generate(
            build_thesis_set(invalidated)
        )


def test_duplicate_recommendations_are_merged() -> None:
    thesis_a = build_thesis(
        identifier="thesis-a",
        title="Thesis A",
    )
    thesis_b = build_thesis(
        identifier="thesis-b",
        title="Thesis B",
    )

    recommendation_a = build_recommendation(
        identifier="credit-recommendation-a",
        source_thesis_identifier="thesis-a",
        confidence=0.80,
        magnitude=RecommendationMagnitude.MODERATE,
        supporting_evidence=("Evidence A",),
    )
    recommendation_b = build_recommendation(
        identifier="credit-recommendation-b",
        source_thesis_identifier="thesis-b",
        confidence=0.90,
        magnitude=RecommendationMagnitude.MODERATE,
        supporting_evidence=("Evidence B",),
    )

    rules = StubRules(
        {
            "thesis-a": (recommendation_a,),
            "thesis-b": (recommendation_b,),
        }
    )

    result = RecommendationEngine(
        rules=rules,  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_a, thesis_b)
    )

    assert len(result.recommendations) == 1

    merged = result.recommendations[0]

    assert merged.confidence == 0.85
    assert merged.supporting_evidence == (
        "Evidence B",
        "Evidence A",
    )


def test_merge_preserves_all_source_thesis_identifiers() -> None:
    thesis_a = build_thesis(
        identifier="thesis-a",
        title="Thesis A",
    )
    thesis_b = build_thesis(
        identifier="thesis-b",
        title="Thesis B",
    )

    rules = StubRules(
        {
            "thesis-a": (
                build_recommendation(
                    identifier="recommendation-a",
                    source_thesis_identifier="thesis-a",
                    confidence=0.80,
                    magnitude=(
                        RecommendationMagnitude.MODERATE
                    ),
                    supporting_evidence=("Evidence A",),
                ),
            ),
            "thesis-b": (
                build_recommendation(
                    identifier="recommendation-b",
                    source_thesis_identifier="thesis-b",
                    confidence=0.90,
                    magnitude=(
                        RecommendationMagnitude.MODERATE
                    ),
                    supporting_evidence=("Evidence B",),
                ),
            ),
        }
    )

    result = RecommendationEngine(
        rules=rules,  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_a, thesis_b)
    )

    assert (
        result.recommendations[0].source_thesis_identifier
        == "thesis-a, thesis-b"
    )


def test_merge_combines_explainability_fields() -> None:
    thesis_a = build_thesis(
        identifier="thesis-a",
        title="Thesis A",
    )
    thesis_b = build_thesis(
        identifier="thesis-b",
        title="Thesis B",
    )

    recommendation_a = build_recommendation(
        identifier="recommendation-a",
        source_thesis_identifier="thesis-a",
        confidence=0.80,
        magnitude=RecommendationMagnitude.MODERATE,
        supporting_evidence=("Evidence A",),
    )
    recommendation_b = build_recommendation(
        identifier="recommendation-b",
        source_thesis_identifier="thesis-b",
        confidence=0.90,
        magnitude=RecommendationMagnitude.MODERATE,
        supporting_evidence=("Evidence B",),
    )

    result = RecommendationEngine(
        rules=StubRules(
            {
                "thesis-a": (recommendation_a,),
                "thesis-b": (recommendation_b,),
            }
        ),  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_a, thesis_b)
    )

    merged = result.recommendations[0]

    assert set(merged.supporting_evidence) == {
        "Evidence A",
        "Evidence B",
    }
    assert set(merged.catalysts) == {
        "Catalyst from thesis-a",
        "Catalyst from thesis-b",
    }
    assert set(merged.risks) == {
        "Risk from thesis-a",
        "Risk from thesis-b",
    }
    assert set(merged.invalidation_conditions) == {
        "Invalidation from thesis-a",
        "Invalidation from thesis-b",
    }


def test_weighted_confidence_uses_magnitude() -> None:
    thesis_a = build_thesis(
        identifier="thesis-a",
        title="Thesis A",
    )
    thesis_b = build_thesis(
        identifier="thesis-b",
        title="Thesis B",
    )

    large = build_recommendation(
        identifier="large-recommendation",
        source_thesis_identifier="thesis-a",
        confidence=0.90,
        magnitude=RecommendationMagnitude.LARGE,
        supporting_evidence=("Large evidence",),
        target="government_bonds",
    )
    small = build_recommendation(
        identifier="small-recommendation",
        source_thesis_identifier="thesis-b",
        confidence=0.50,
        magnitude=RecommendationMagnitude.SMALL,
        supporting_evidence=("Small evidence",),
        target="small_cap_equities",
    )

    result = RecommendationEngine(
        rules=StubRules(
            {
                "thesis-a": (large,),
                "thesis-b": (small,),
            }
        ),  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_a, thesis_b)
    )

    expected = round(
        ((0.90 * 1.50) + (0.50 * 0.75))
        / (1.50 + 0.75),
        4,
    )

    assert result.confidence == expected


def test_recommendations_have_deterministic_order() -> None:
    thesis_a = build_thesis(
        identifier="thesis-a",
        title="Thesis A",
    )
    thesis_b = build_thesis(
        identifier="thesis-b",
        title="Thesis B",
    )

    macro = build_recommendation(
        identifier="macro-recommendation",
        source_thesis_identifier="thesis-a",
        confidence=0.60,
        magnitude=RecommendationMagnitude.SMALL,
        supporting_evidence=("Macro evidence",),
        target="recession_protection",
        level=RecommendationLevel.MACRO,
    )
    sector = build_recommendation(
        identifier="sector-recommendation",
        source_thesis_identifier="thesis-b",
        confidence=0.95,
        magnitude=RecommendationMagnitude.LARGE,
        supporting_evidence=("Sector evidence",),
        target="industrials",
        level=RecommendationLevel.SECTOR,
    )

    rules = StubRules(
        {
            "thesis-a": (macro,),
            "thesis-b": (sector,),
        }
    )

    result_one = RecommendationEngine(
        rules=rules,  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_a, thesis_b)
    )

    result_two = RecommendationEngine(
        rules=rules,  # type: ignore[arg-type]
    ).generate(
        build_thesis_set(thesis_b, thesis_a)
    )

    identifiers_one = tuple(
        recommendation.identifier
        for recommendation in result_one.recommendations
    )
    identifiers_two = tuple(
        recommendation.identifier
        for recommendation in result_two.recommendations
    )

    assert identifiers_one == identifiers_two
    assert identifiers_one == (
        "macro-recommendation",
        "sector-recommendation",
    )


def test_summary_contains_key_decision_information() -> None:
    thesis = build_thesis(
        identifier="higher-quality-credit-outperforms",
        title="Higher-Quality Credit Outperforms",
    )

    result = RecommendationEngine().generate(
        build_thesis_set(thesis)
    )

    assert "Total Recommendations:" in result.summary
    assert "Recommendation Levels" in result.summary
    assert "Allocation Tilt" in result.summary
    assert "Highest Conviction" in result.summary
    assert (
        "Overall Recommendation Confidence:"
        in result.summary
    )
