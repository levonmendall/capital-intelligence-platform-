"""Build a normalized market snapshot from economic data."""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.models import MarketSnapshot
from intelligence.provider import load_sample_snapshot
from providers.fred import FREDProvider, FREDProviderError


@dataclass(frozen=True)
class EconomicReadings:
    """Raw economic observations used by the regime engine."""

    unemployment_rate: float
    inflation_rate: float
    ten_year_yield: float
    two_year_yield: float
    federal_funds_rate: float


SERIES = {
    "unemployment": "UNRATE",
    "inflation": "CPIAUCSL",
    "ten_year": "DGS10",
    "two_year": "DGS2",
    "fed_funds": "FEDFUNDS",
}


def clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    """Restrict a number to the configured normalized range."""

    return max(minimum, min(maximum, value))


def build_live_snapshot(
    provider: FREDProvider | None = None,
) -> tuple[MarketSnapshot, EconomicReadings]:
    """Create a normalized snapshot from current FRED readings."""

    fred = provider or FREDProvider()

    unemployment = fred.get_latest_value(
        SERIES["unemployment"]
    ).value
    inflation_observations = fred.get_observations(
        SERIES["inflation"],
        limit=14,
    )
    ten_year = fred.get_latest_value(
        SERIES["ten_year"]
    ).value
    two_year = fred.get_latest_value(
        SERIES["two_year"]
    ).value
    fed_funds = fred.get_latest_value(
        SERIES["fed_funds"]
    ).value

    latest_cpi = inflation_observations[0].value
    year_ago_cpi = inflation_observations[-1].value

    inflation_rate = (
        (latest_cpi / year_ago_cpi) - 1
    ) * 100

    yield_spread = ten_year - two_year

    growth_score = clamp((5.0 - unemployment) / 3.0)
    inflation_score = clamp((inflation_rate - 2.0) / 3.0)
    trend_score = clamp(yield_spread / 2.0)
    volatility_score = clamp((fed_funds - 3.0) / 4.0)
    credit_score = clamp(-yield_spread / 2.0)

    snapshot = MarketSnapshot(
        growth=growth_score,
        inflation=inflation_score,
        trend=trend_score,
        volatility=volatility_score,
        credit=credit_score,
    )

    readings = EconomicReadings(
        unemployment_rate=unemployment,
        inflation_rate=inflation_rate,
        ten_year_yield=ten_year,
        two_year_yield=two_year,
        federal_funds_rate=fed_funds,
    )

    return snapshot, readings


def load_best_available_snapshot() -> tuple[MarketSnapshot, str]:
    """Use live FRED data when configured, otherwise use sample data."""

    provider = FREDProvider()

    if not provider.configured:
        return load_sample_snapshot(), "Sample data"

    try:
        snapshot, _ = build_live_snapshot(provider)
        return snapshot, "Live FRED data"
    except FREDProviderError:
        return load_sample_snapshot(), "Sample fallback"
