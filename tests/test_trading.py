"""Tests for the paper trading engine."""

from core.database import initialize_database
from core.seed import seed_mandates
from core.trading import (
    place_trade,
    update_holding_price,
)
from core.portfolio import (
    get_holdings,
    get_mandate_details,
)


def setup_module(module):
    initialize_database()
    seed_mandates()


def test_buy_trade():
    result = place_trade(
        mandate_code="CP",
        side="BUY",
        symbol="SPY",
        quantity=10,
        price=100,
        rationale="Unit Test",
    )

    assert result.remaining_cash == 24000


def test_update_price():
    update_holding_price(
        "CP",
        "SPY",
        110,
    )

    holdings = get_holdings("CP")

    assert holdings[0]["current_price"] == 110


def test_portfolio_gain():
    details = get_mandate_details("CP")

    assert details["nav"] == 25100
