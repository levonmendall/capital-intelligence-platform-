"""Transparent market-regime classification compatibility facade."""

from economic_regime import (
    EconomicRegimeEngine,
    EconomicRegimeInputs,
    EconomicRegimeResult,
)
from intelligence.models import MarketSnapshot


def determine_regime(snapshot: MarketSnapshot) -> tuple[str, float]:
    """Return the legacy allocation regime and confidence level.

    This public function remains stable for the existing allocation pipeline.
    New institutional consumers should call :func:`evaluate_economic_regime`.
    """

    expansion_score = (
        snapshot.growth
        + snapshot.trend
        - snapshot.inflation
        - snapshot.volatility
        - snapshot.credit
    )

    if expansion_score >= 1.0:
        return "Expansion", 0.82

    if expansion_score >= 0.55:
        return "Recovery", 0.74

    if snapshot.inflation >= 0.65:
        return "Inflation Shock", 0.77

    if snapshot.growth <= -0.40 and snapshot.trend <= -0.30:
        return "Recession", 0.80

    return "Slowdown", 0.68


def evaluate_economic_regime(
    snapshot: MarketSnapshot,
    *,
    policy: float | None = None,
    liquidity: float | None = None,
    financial_stress: float | None = None,
) -> EconomicRegimeResult:
    """Map the legacy snapshot into the institutional regime engine."""

    if not isinstance(snapshot, MarketSnapshot):
        raise TypeError("snapshot must be a MarketSnapshot")

    return EconomicRegimeEngine().evaluate(
        EconomicRegimeInputs(
            growth=snapshot.growth,
            inflation=snapshot.inflation,
            policy=policy,
            liquidity=liquidity,
            financial_stress=(
                snapshot.volatility
                if financial_stress is None
                else financial_stress
            ),
        )
    )
