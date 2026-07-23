"""Tests for the investment thesis engine."""

import pytest

from intelligence.theme import (
    EconomicTheme,
    ThemeCategory,
    ThemeDirection,
    ThemeSet,
)
from intelligence.thesis import (
    InvestmentThesis,
    InvestmentThesisSet,
    ThesisDirection,
    ThesisHorizon,
    ThesisStatus,
)
from intelligence.thesis_engine import (
    InvestmentThesisEngine,
)


def build_theme(
    *,
    identifier: str = "disinflation-with-positive-growth",
    title: str = "Disinflation With Positive Growth",
    category: ThemeCategory = ThemeCategory.INFLATION,
    direction: ThemeDirection = ThemeDirection.POSITIVE,
    confidence: float = 0.78,
    duration: int = 12,
) -> EconomicTheme:
    return EconomicTheme(
        identifier=identifier,
        title=title,
        category=category,
        direction=direction,
        confidence=confidence,
        description="Economic theme used for testing.",
        supporting_evidence=(
            "Forecast evidence supports the theme.",
            "Current-state evidence supports the theme.",
        ),
        risks=(
            "The theme may reverse.",
        ),
        affected_asset_classes=(
            "equities",
            "government_bonds",
        ),
        expected_duration_months=duration,
    )


def build_theme_set(
    *themes: EconomicTheme,
) -> ThemeSet:
    selected_themes = themes or (
        build_theme(),
    )

    return ThemeSet(
        themes=tuple(selected_themes),
        confidence=0.76,
        summary="Theme set used for testing.",
    )


def test_disinflation_theme_generates_expected_thesis() -> None:
    result = InvestmentThesisEngine().generate(
        build_theme_set()
    )

    assert len(result.theses) == 1

    thesis = result.theses[0]

    assert (
        thesis.identifier
        == "long-duration-quality-in-disinflation"
    )
    assert thesis.direction == ThesisDirection.BULLISH
    assert thesis.status == ThesisStatus.ACTIVE
    assert thesis.source_theme_identifier == (
        "disinflation-with-positive-growth"
    )
    assert thesis.beneficiaries
    assert thesis.invalidation_conditions


def test_defensive_theme_generates_bearish_thesis() -> None:
    theme = build_theme(
        identifier="defensive-positioning",
        title="Defensive Positioning",
        category=ThemeCategory.DEFENSIVE,
        direction=ThemeDirection.POSITIVE,
        confidence=0.80,
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(theme)
    )

    thesis = result.theses[0]

    assert (
        thesis.identifier
        == "defensive-assets-during-contraction"
    )
    assert thesis.direction == ThesisDirection.BEARISH
    assert "government_bonds" in thesis.beneficiaries
    assert "cyclical_equities" in thesis.losers


def test_credit_theme_generates_selective_thesis() -> None:
    theme = build_theme(
        identifier="credit-quality-differentiation",
        title="Credit Quality Differentiation",
        category=ThemeCategory.CREDIT,
        direction=ThemeDirection.NEGATIVE,
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(theme)
    )

    thesis = result.theses[0]

    assert (
        thesis.identifier
        == "higher-quality-credit-outperforms"
    )
    assert thesis.direction == ThesisDirection.SELECTIVE
    assert "investment_grade_bonds" in thesis.beneficiaries
    assert "high_yield_bonds" in thesis.losers


def test_manufacturing_theme_generates_tactical_thesis() -> None:
    theme = build_theme(
        identifier="manufacturing-weakness",
        title="Manufacturing Weakness",
        category=ThemeCategory.MANUFACTURING,
        direction=ThemeDirection.NEGATIVE,
        duration=6,
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(theme)
    )

    thesis = result.theses[0]

    assert thesis.horizon == ThesisHorizon.TACTICAL
    assert thesis.direction == ThesisDirection.BEARISH


def test_unknown_theme_uses_generic_builder() -> None:
    theme = build_theme(
        identifier="new-structural-theme",
        title="New Structural Theme",
        category=ThemeCategory.STRUCTURAL,
        direction=ThemeDirection.MIXED,
        duration=36,
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(theme)
    )

    thesis = result.theses[0]

    assert thesis.identifier == (
        "new-structural-theme-investment-implication"
    )
    assert thesis.direction == ThesisDirection.SELECTIVE
    assert thesis.horizon == ThesisHorizon.STRUCTURAL


def test_multiple_themes_generate_multiple_theses() -> None:
    themes = (
        build_theme(),
        build_theme(
            identifier="manufacturing-weakness",
            title="Manufacturing Weakness",
            category=ThemeCategory.MANUFACTURING,
            direction=ThemeDirection.NEGATIVE,
            duration=6,
        ),
        build_theme(
            identifier="material-recession-tail-risk",
            title="Material Recession Tail Risk",
            category=ThemeCategory.DEFENSIVE,
            direction=ThemeDirection.NEGATIVE,
        ),
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(*themes)
    )

    assert len(result.theses) == 3
    assert "3 investment theses" in result.summary


def test_thesis_set_filters_by_direction() -> None:
    themes = (
        build_theme(),
        build_theme(
            identifier="manufacturing-weakness",
            title="Manufacturing Weakness",
            category=ThemeCategory.MANUFACTURING,
            direction=ThemeDirection.NEGATIVE,
            duration=6,
        ),
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(*themes)
    )

    bullish = result.by_direction(
        ThesisDirection.BULLISH
    )

    bearish = result.by_direction(
        ThesisDirection.BEARISH
    )

    assert bullish
    assert bearish


def test_thesis_set_filters_by_source_theme() -> None:
    result = InvestmentThesisEngine().generate(
        build_theme_set()
    )

    matching = result.by_theme(
        "disinflation-with-positive-growth"
    )

    assert len(matching) == 1
    assert matching[0].source_theme_identifier == (
        "disinflation-with-positive-growth"
    )


def test_thesis_set_returns_highest_confidence() -> None:
    themes = (
        build_theme(
            confidence=0.60,
        ),
        build_theme(
            identifier="manufacturing-weakness",
            title="Manufacturing Weakness",
            category=ThemeCategory.MANUFACTURING,
            direction=ThemeDirection.NEGATIVE,
            confidence=0.90,
            duration=6,
        ),
    )

    result = InvestmentThesisEngine().generate(
        build_theme_set(*themes)
    )

    highest = result.highest_confidence()

    assert highest.confidence == max(
        thesis.confidence
        for thesis in result.theses
    )


def test_thesis_model_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        InvestmentThesis(
            identifier="invalid-thesis",
            title="Invalid Thesis",
            source_theme_identifier="source-theme",
            source_theme_category=ThemeCategory.GROWTH,
            direction=ThesisDirection.NEUTRAL,
            horizon=ThesisHorizon.TACTICAL,
            status=ThesisStatus.ACTIVE,
            confidence=1.50,
            proposition="Invalid confidence test.",
            supporting_evidence=("Evidence.",),
            contradicting_evidence=(),
            beneficiaries=("equities",),
            losers=(),
            catalysts=("Catalyst.",),
            risks=("Risk.",),
            increase_conviction_conditions=("Increase.",),
            reduce_conviction_conditions=("Reduce.",),
            invalidation_conditions=("Invalidation.",),
            expected_duration_months=12,
        )


def test_thesis_set_rejects_duplicate_identifiers() -> None:
    theme = build_theme()

    thesis = InvestmentThesisEngine().generate(
        build_theme_set(theme)
    ).theses[0]

    with pytest.raises(ValueError):
        InvestmentThesisSet(
            theses=(thesis, thesis),
            confidence=0.75,
            summary="Duplicate thesis test.",
        )


def test_thesis_engine_rejects_wrong_input_type() -> None:
    with pytest.raises(TypeError):
        InvestmentThesisEngine().generate(
            "not a theme set"  # type: ignore[arg-type]
        )
