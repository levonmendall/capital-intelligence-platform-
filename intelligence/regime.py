"""
Determines the current market regime.
"""

from intelligence.models import MarketRegime


def determine_regime(snapshot):

    score = (
        snapshot.growth
        + snapshot.trend
        - snapshot.volatility
        - snapshot.inflation
    )

    if score > 0.75:
        return MarketRegime(
            "Expansion",
            0.82,
            "Economic growth is strong with favorable market conditions."
        )

    if score > 0.35:
        return MarketRegime(
            "Recovery",
            0.73,
            "Growth is improving while risks remain moderate."
        )

    return MarketRegime(
        "Slowdown",
        0.68,
        "Risk assets should be approached cautiously."
    )
