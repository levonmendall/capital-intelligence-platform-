"""Tests for the economic theme engine."""

import pytest

from intelligence.forecast import (
    EconomicForecast,
    EconomicScenario,
    ScenarioForecast,
)
from intelligence.state import (
    Direction,
    EconomicState,
    Strength,
)
from intelligence.theme import (
    EconomicTheme,
    ThemeCategory,
    ThemeDirection,
    ThemeSet,
)
from intelligence.theme_engine import ThemeEngine


def build_state(
    *,
    growth: Strength = Strength.MODERATE,
    inflation: Direction = Direction.IMPROVING,
    labor_market: Strength = Strength.STRONG,
    credit: Direction = Direction.STABLE,
    liquidity: Direction = Direction.STABLE,
    manufacturing: Direction = Direction.STABLE,
    housing: Direction = Direction.STABLE,
    consumer: Strength = Strength.MODERATE,
    confidence: float = 0.82,
) -> EconomicState:
    return EconomicState(
        growth=growth,
        inflation=inflation,
        labor_market=labor_market,
        credit=credit,
        liquidity=liquidity,
        manufacturing=manufacturing,
        housing=housing,
        consumer=consumer,
        confidence=confidence,
        summary="Current economic conditions were evaluated.",
    )


def build_forecast(
    *,
    state: EconomicState | None = None,
    soft_landing: float = 0.60,
    recession: float = 0.20,
    reacceleration: float = 0.15,
    stagflation: float = 0.05,
    confidence: float = 0.75,
) -> EconomicForecast:
    current_state = state or build_state()

    return EconomicForecast(
        current_state=current_state,
        scenarios=(
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=soft_landing,
                rationale="Soft landing rationale.",
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=recession,
                rationale="Recession rationale.",
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=reacceleration,
                rationale="Reacceleration rationale.",
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=stagflation,
                rationale="Stagflation rationale.",
            ),
        ),
        confidence=confidence,
        summary="Economic forecast summary.",
        horizon_months=12,
    )


def test_soft_landing_forecast_generates_soft_landing_themes() -> None:
    forecast = build_forecast()

    result = ThemeEngine().generate(forecast)

    identifiers = {
        theme.identifier
        for theme in result.themes
    }

    assert "disinflation-with-positive-growth" in identifiers
    assert "quality-risk-assets-supported" in identifiers
    assert result.confidence > 0.0
    assert result.summary


def test_recession_forecast_generates_defensive_theme() -> None:
    state = build_state(
        growth=Strength.WEAK,
        labor_market=Strength.WEAK,
        credit=Direction.DETERIORATING,
        manufacturing=Direction.DETERIORATING,
        consumer=Strength.WEAK,
    )

    forecast = build_forecast(
        state=state,
        soft_landing=0.15,
        recession=0.60,
        reacceleration=0.10,
        stagflation=0.15,
    )

    result = ThemeEngine().generate(forecast)

    identifiers = {
        theme.identifier
        for theme in result.themes
    }

    assert "defensive-positioning" in identifiers
    assert "credit-quality-differentiation" in identifiers
    assert "tightening-credit-conditions" in identifiers


def test_reacceleration_forecast_generates_cyclical_theme() -> None:
    state = build_state(
        growth=Strength.STRONG,
        labor_market=Strength.STRONG,
        manufacturing=Direction.IMPROVING,
        consumer=Strength.STRONG,
    )

    forecast = build_forecast(
        state=state,
        soft_landing=0.20,
        recession=0.10,
        reacceleration=0.60,
        stagflation=0.10,
    )

    result = ThemeEngine().generate(forecast)

    identifiers = {
        theme.identifier
        for theme in result.themes
    }

    assert "cyclical-growth-leadership" in identifiers
    assert "higher-for-longer-rate-risk" in identifiers
    assert "resilient-household-demand" in identifiers


def test_stagflation_forecast_generates_inflation_theme() -> None:
    state = build_state(
        growth=Strength.WEAK,
        inflation=Direction.DETERIORATING,
        manufacturing=Direction.DETERIORATING,
    )

    forecast = build_forecast(
        state=state,
        soft_landing=0.15,
        recession=0.20,
        reacceleration=0.10,
        stagflation=0.55,
    )

    result = ThemeEngine().generate(forecast)

    identifiers = {
        theme.identifier
        for theme in result.themes
    }

    assert "inflation-resilience" in identifiers
    assert "margin-pressure" in identifiers


def test_material_recession_risk_is_preserved() -> None:
    forecast = build_forecast(
        soft_landing=0.40,
        recession=0.30,
        reacceleration=0.15,
        stagflation=0.15,
    )

    result = ThemeEngine().generate(forecast)

    identifiers = {
        theme.identifier
        for theme in result.themes
    }

    assert "material-recession-tail-risk" in identifiers


def test_theme_set_can_filter_by_category() -> None:
    result = ThemeEngine().generate(
        build_forecast()
    )

    inflation_themes = result.by_category(
        ThemeCategory.INFLATION
    )

    assert inflation_themes
    assert all(
        theme.category == ThemeCategory.INFLATION
        for theme in inflation_themes
    )


def test_theme_set_returns_highest_confidence_theme() -> None:
    result = ThemeEngine().generate(
        build_forecast()
    )

    highest = result.highest_confidence()

    assert highest in result.themes
    assert highest.confidence == max(
        theme.confidence
        for theme in result.themes
    )


def test_theme_model_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        EconomicTheme(
            identifier="invalid-theme",
            title="Invalid Theme",
            category=ThemeCategory.GROWTH,
            direction=ThemeDirection.NEUTRAL,
            confidence=1.50,
            description="Invalid confidence test.",
            supporting_evidence=("Evidence.",),
            risks=("Risk.",),
            affected_asset_classes=("equities",),
            expected_duration_months=12,
        )


def test_theme_set_rejects_duplicate_identifiers() -> None:
    theme = EconomicTheme(
        identifier="duplicate-theme",
        title="Duplicate Theme",
        category=ThemeCategory.GROWTH,
        direction=ThemeDirection.NEUTRAL,
        confidence=0.50,
        description="Duplicate identifier test.",
        supporting_evidence=("Evidence.",),
        risks=("Risk.",),
        affected_asset_classes=("equities",),
        expected_duration_months=12,
    )

    with pytest.raises(ValueError):
        ThemeSet(
            themes=(theme, theme),
            confidence=0.50,
            summary="Duplicate test.",
        )


def test_theme_engine_rejects_wrong_input_type() -> None:
    with pytest.raises(TypeError):
        ThemeEngine().generate("not a forecast")  # type: ignore[arg-type]
