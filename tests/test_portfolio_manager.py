"""Tests for the AI Portfolio Manager."""

from intelligence.portfolio_manager import (
    determine_model,
    load_model_portfolios,
)


def test_model_file_loads():

    models = load_model_portfolios()

    assert "Defensive" in models
    assert "Balanced" in models
    assert "Growth" in models


def test_recession():

    assert (
        determine_model("Recession")
        == "Defensive"
    )


def test_recovery():

    assert (
        determine_model("Recovery")
        == "Growth"
    )


def test_slowdown():

    assert (
        determine_model("Slowdown")
        == "Balanced"
    )
