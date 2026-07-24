"""Tests for the institutional economic-regime bounded context."""

import pytest

from economic_regime import (
    EconomicRegimeEngine,
    EconomicRegimeInputs,
    Regime,
)
from intelligence.models import MarketSnapshot
from intelligence.regime import evaluate_economic_regime


@pytest.mark.parametrize(
    ("inputs", "expected"),
    [
        (
            EconomicRegimeInputs(
                growth=0.60,
                inflation=-0.10,
                policy=0.10,
                liquidity=0.40,
                financial_stress=-0.30,
            ),
            Regime.GOLDILOCKS,
        ),
        (
            EconomicRegimeInputs(
                growth=0.55,
                inflation=0.55,
                policy=0.30,
                liquidity=0.30,
                financial_stress=0.10,
            ),
            Regime.REFLATION,
        ),
        (
            EconomicRegimeInputs(
                growth=-0.15,
                inflation=0.70,
                policy=0.65,
                liquidity=-0.25,
                financial_stress=0.30,
            ),
            Regime.STAGFLATION,
        ),
        (
            EconomicRegimeInputs(
                growth=0.10,
                inflation=-0.35,
                policy=0.20,
                liquidity=-0.10,
                financial_stress=0.15,
            ),
            Regime.DISINFLATIONARY_SLOWDOWN,
        ),
        (
            EconomicRegimeInputs(
                growth=-0.70,
                inflation=-0.10,
                policy=0.40,
                liquidity=-0.65,
                financial_stress=0.80,
            ),
            Regime.CONTRACTION,
        ),
        (
            EconomicRegimeInputs(
                growth=0.10,
                inflation=0.20,
                policy=0.10,
                liquidity=0.10,
                financial_stress=0.10,
            ),
            Regime.TRANSITION,
        ),
    ],
)
def test_classifies_supported_regimes(inputs, expected) -> None:
    result = EconomicRegimeEngine().evaluate(inputs)

    assert result.regime == expected
    assert 0.0 <= result.confidence <= 1.0
    assert result.data_coverage == 1.0
    assert len(result.signals) == 5
    assert result.conclusion


def test_missing_data_reduces_coverage_and_forces_transition() -> None:
    result = EconomicRegimeEngine().evaluate(
        EconomicRegimeInputs(
            growth=0.60,
            inflation=None,
            policy=None,
            liquidity=0.40,
            financial_stress=None,
        )
    )

    assert result.regime == Regime.TRANSITION
    assert result.data_coverage == 0.4
    assert result.confidence < 0.65
    assert any("Missing inflation data" in risk for risk in result.risks)


def test_mapping_input_is_supported() -> None:
    result = EconomicRegimeEngine().evaluate(
        {
            "growth": 0.5,
            "inflation": 0.1,
            "policy": 0.0,
            "liquidity": 0.2,
            "financial_stress": 0.0,
        }
    )

    assert result.regime == Regime.GOLDILOCKS


def test_out_of_range_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="growth"):
        EconomicRegimeInputs(growth=1.01, inflation=0.0)


def test_legacy_snapshot_compatibility_facade() -> None:
    snapshot = MarketSnapshot(
        growth=0.55,
        inflation=0.20,
        trend=0.60,
        volatility=0.10,
        credit=-0.20,
    )

    result = evaluate_economic_regime(
        snapshot,
        policy=0.20,
        liquidity=0.35,
    )

    assert result.regime == Regime.GOLDILOCKS
    assert result.data_coverage == 1.0
