"""Tests for the paper-trading engine."""

import pytest

from core.portfolio import (
    get_holdings,
    get_mandate_details,
)
from core.trading import (
    TradingError,
    place_trade,
    update_holding_price,
)


def test_buy_trade() -> None:
    """A valid purchase should reduce mandate cash."""

    result = place_trade(
        mandate_code="CP",
        side="BUY",
        symbol="SPY",
        quantity=10,
        price=100,
        rationale="Unit test purchase",
    )

    assert result.remaining_cash == 24000

    holdings = get_holdings("CP")

    assert len(holdings) == 1
    assert holdings[0]["symbol"] == "SPY"
    assert holdings[0]["quantity"] == 10
    assert holdings[0]["average_cost"] == 100


def test_update_price() -> None:
    """Updating a holding price should change its market value."""

    place_trade(
        mandate_code="CP",
        side="BUY",
        symbol="SPY",
        quantity=10,
        price=100,
        rationale="Create holding for price test",
    )

    update_holding_price(
        mandate_code="CP",
        symbol="SPY",
        price=110,
    )

    holdings = get_holdings("CP")

    assert len(holdings) == 1
    assert holdings[0]["current_price"] == 110
    assert holdings[0]["market_value"] == 1100
    assert holdings[0]["unrealized_gain"] == 100


def test_portfolio_gain() -> None:
    """A price increase should raise the mandate NAV."""

    place_trade(
        mandate_code="CP",
        side="BUY",
        symbol="SPY",
        quantity=10,
        price=100,
        rationale="Create holding for performance test",
    )

    update_holding_price(
        mandate_code="CP",
        symbol="SPY",
        price=110,
    )

    details = get_mandate_details("CP")

    assert details is not None
    assert details["nav"] == 25100
    assert details["total_return"] == pytest.approx(0.004)


def test_rejects_purchase_without_enough_cash() -> None:
    """A mandate cannot purchase more than its available cash."""

    with pytest.raises(TradingError):
        place_trade(
            mandate_code="CP",
            side="BUY",
            symbol="SPY",
            quantity=1000,
            price=100,
            rationale="Invalid oversized purchase",
        )


def test_rejects_sale_without_shares() -> None:
    """A mandate cannot sell shares it does not own."""

    with pytest.raises(TradingError):
        place_trade(
            mandate_code="CP",
            side="SELL",
            symbol="SPY",
            quantity=1,
            price=100,
            rationale="Invalid sale",
        )
