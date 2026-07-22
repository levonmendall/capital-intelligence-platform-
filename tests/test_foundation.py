"""Foundation tests for the Capital Intelligence Platform."""

from core.database import initialize_database
from core.portfolio import get_mandates, get_portfolio_totals
from intelligence.pipeline import build_allocation, run_intelligence
from intelligence.provider import load_sample_snapshot
from intelligence.regime import determine_regime


def test_platform_has_eight_mandates() -> None:
    """Confirm all configured mandates load successfully."""

    initialize_database()
    mandates = get_mandates()

    assert len(mandates) == 8


def test_total_virtual_capital_is_200000() -> None:
    """Confirm the eight mandates total $200,000."""

    totals = get_portfolio_totals()

    assert totals["starting_capital"] == 200000
    assert totals["cash"] == 200000
    assert totals["nav"] == 200000


def test_sample_snapshot_loads() -> None:
    """Confirm sample market information loads correctly."""

    snapshot = load_sample_snapshot()

    assert snapshot.growth == 0.55
    assert snapshot.inflation == 0.20
    assert snapshot.trend == 0.60


def test_regime_engine_returns_valid_result() -> None:
    """Confirm the regime engine returns a supported regime."""

    snapshot = load_sample_snapshot()
    regime, confidence = determine_regime(snapshot)

    valid_regimes = {
        "Expansion",
        "Recovery",
        "Slowdown",
        "Recession",
        "Inflation Shock",
    }

    assert regime in valid_regimes
    assert 0 <= confidence <= 1


def test_allocations_total_one_hundred_percent() -> None:
    """Confirm every model allocation totals 100%."""

    regimes = [
        "Expansion",
        "Recovery",
        "Slowdown",
        "Recession",
        "Inflation Shock",
    ]

    for regime in regimes:
        _, allocation = build_allocation(regime)

        assert abs(sum(allocation.values()) - 1.0) < 0.000001


def test_intelligence_pipeline_returns_decision() -> None:
    """Confirm the complete intelligence pipeline works."""

    decision = run_intelligence(save=False)

    assert decision.regime
    assert decision.risk_posture
    assert decision.rationale
    assert 0 <= decision.confidence <= 1

    total_allocation = (
        decision.equities
        + decision.bonds
        + decision.cash
        + decision.alternatives
    )

    assert abs(total_allocation - 1.0) < 0.000001
