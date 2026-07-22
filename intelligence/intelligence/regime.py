"""Transparent market-regime classification engine."""

from intelligence.models import MarketSnapshot


def determine_regime(snapshot: MarketSnapshot) -> tuple[str, float]:
    """Determine the most likely market regime and confidence level."""

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
