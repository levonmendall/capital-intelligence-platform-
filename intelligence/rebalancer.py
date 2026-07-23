"""Portfolio rebalancing engine."""

from __future__ import annotations

from dataclasses import dataclass

from core.portfolio import get_holdings, get_mandate_details
from intelligence.portfolio_manager import (
    build_trade_recommendations,
)


@dataclass(frozen=True)
class RebalanceAction:
    """A recommended rebalance trade."""

    symbol: str
    current_weight: float
    target_weight: float
    difference: float
    action: str


def calculate_rebalance(mandate_code: str):
    """
    Compare the current portfolio against the AI model.
    """

    mandate = get_mandate_details(mandate_code)

    if mandate is None:
        raise ValueError(
            f"Unknown mandate: {mandate_code}"
        )

    nav = float(mandate["nav"])

    holdings = get_holdings(mandate_code)

    current_weights = {}

    for holding in holdings:

        market_value = float(
            holding["market_value"]
        )

        current_weights[
            holding["symbol"]
        ] = market_value / nav if nav else 0

    recommendations = (
        build_trade_recommendations()
    )

    target_weights = {
        recommendation.symbol:
        recommendation.target_weight
        for recommendation in
        recommendations["recommendations"]
    }

    symbols = sorted(
        set(current_weights)
        | set(target_weights)
    )

    actions = []

    tolerance = 0.01

    for symbol in symbols:

        current = current_weights.get(
            symbol,
            0.0,
        )

        target = target_weights.get(
            symbol,
            0.0,
        )

        difference = target - current

        if abs(difference) < tolerance:
            action = "HOLD"
        elif difference > 0:
            action = "BUY"
        else:
            action = "SELL"

        actions.append(
            RebalanceAction(
                symbol=symbol,
                current_weight=current,
                target_weight=target,
                difference=difference,
                action=action,
            )
        )

    return actions
