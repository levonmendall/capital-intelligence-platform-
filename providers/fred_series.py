"""Canonical FRED series specifications used by the foundation."""

from datetime import timedelta
from types import MappingProxyType

from data import (
    DataFrequency,
    SeriesSpecification,
    Transformation,
)


FRED_SERIES = MappingProxyType(
    {
        "unemployment": SeriesSpecification(
            provider_series_identifier="UNRATE",
            indicator="unemployment",
            category="labor",
            unit="percent",
            frequency=DataFrequency.MONTHLY,
            stale_after=timedelta(days=45),
            importance=1.0,
        ),
        "consumer_price_index": SeriesSpecification(
            provider_series_identifier="CPIAUCSL",
            indicator="consumer_price_index",
            category="inflation",
            unit="index",
            frequency=DataFrequency.MONTHLY,
            transformation=Transformation.LEVEL,
            stale_after=timedelta(days=45),
            importance=1.0,
        ),
        "industrial_production": SeriesSpecification(
            provider_series_identifier="INDPRO",
            indicator="industrial_production",
            category="growth",
            unit="index",
            frequency=DataFrequency.MONTHLY,
            transformation=Transformation.LEVEL,
            stale_after=timedelta(days=45),
            importance=1.0,
        ),
        "ten_year_treasury": SeriesSpecification(
            provider_series_identifier="DGS10",
            indicator="ten_year_treasury_yield",
            category="rates",
            unit="percent",
            frequency=DataFrequency.DAILY,
            stale_after=timedelta(days=5),
            importance=0.9,
        ),
        "two_year_treasury": SeriesSpecification(
            provider_series_identifier="DGS2",
            indicator="two_year_treasury_yield",
            category="rates",
            unit="percent",
            frequency=DataFrequency.DAILY,
            stale_after=timedelta(days=5),
            importance=0.9,
        ),
        "federal_funds_rate": SeriesSpecification(
            provider_series_identifier="FEDFUNDS",
            indicator="federal_funds_rate",
            category="policy",
            unit="percent",
            frequency=DataFrequency.MONTHLY,
            stale_after=timedelta(days=45),
            importance=1.0,
        ),
        "federal_reserve_total_assets": SeriesSpecification(
            provider_series_identifier="WALCL",
            indicator="federal_reserve_total_assets",
            category="liquidity",
            unit="millions_of_us_dollars",
            frequency=DataFrequency.WEEKLY,
            transformation=Transformation.LEVEL,
            stale_after=timedelta(days=14),
            importance=0.9,
        ),
        "financial_stress_index": SeriesSpecification(
            provider_series_identifier="STLFSI4",
            indicator="financial_stress_index",
            category="financial_stress",
            unit="index",
            frequency=DataFrequency.WEEKLY,
            transformation=Transformation.LEVEL,
            stale_after=timedelta(days=14),
            importance=1.0,
        ),
    }
)

__all__ = ["FRED_SERIES"]
