"""Tests for provider-neutral equity and crypto market-data contracts."""

from datetime import datetime, timedelta, timezone

import pytest

from data import (
    BarInterval,
    CanonicalMarketDataProvider,
    CorporateAction,
    CorporateActionType,
    DataQualityState,
    FundingRate,
    MarketDataBatch,
    MarketDataProvenance,
    MarketDataQuery,
    MarketDataType,
    MarketQuote,
    OpenInterest,
    PriceBar,
)


AS_OF = datetime(2025, 2, 3, 16, 0, tzinfo=timezone.utc)


def provenance(
    *,
    venue: str = "NASDAQ",
    observed_at: datetime = AS_OF,
) -> MarketDataProvenance:
    """Return deterministic live provenance."""

    return MarketDataProvenance(
        provider="fixture",
        venue=venue,
        observed_at=observed_at,
        retrieved_at=observed_at + timedelta(seconds=1),
        quality_state=DataQualityState.FIXTURE,
        provider_record_id="record-1",
    )


def test_equity_quote_and_bar_preserve_venue_and_time() -> None:
    instrument_id = (
        "SEC:CIK:0000320193:LISTING:NASDAQ:AAPL"
    )
    quote = MarketQuote(
        instrument_id=instrument_id,
        currency="usd",
        bid=229.90,
        ask=230.10,
        last=230.0,
        bid_size=100,
        ask_size=80,
        provenance=provenance(),
    )
    bar = PriceBar(
        instrument_id=instrument_id,
        currency="usd",
        interval=BarInterval.DAY,
        start_at=AS_OF - timedelta(days=1),
        end_at=AS_OF,
        open=225,
        high=232,
        low=224,
        close=230,
        volume=40_000_000,
        provenance=provenance(),
    )

    assert quote.currency == "USD"
    assert quote.provenance.provider == "FIXTURE"
    assert bar.high == 232.0
    assert bar.volume == 40_000_000.0


def test_crypto_derivatives_are_venue_specific() -> None:
    instrument_id = "CRYPTO:BTC-USDT:PERPETUAL"
    observed_at = datetime(
        2025,
        2,
        3,
        8,
        0,
        tzinfo=timezone.utc,
    )
    crypto_provenance = provenance(
        venue="crypto_venue",
        observed_at=observed_at,
    )
    funding = FundingRate(
        instrument_id=instrument_id,
        currency="usdt",
        period_start=observed_at - timedelta(hours=8),
        period_end=observed_at,
        rate=0.0001,
        provenance=crypto_provenance,
    )
    open_interest = OpenInterest(
        instrument_id=instrument_id,
        currency="usdt",
        value=1_250_000_000,
        provenance=crypto_provenance,
    )

    assert funding.rate == pytest.approx(0.0001)
    assert funding.provenance.venue == "CRYPTO_VENUE"
    assert open_interest.value == 1_250_000_000.0


def test_batch_enforces_point_in_time_boundary() -> None:
    instrument_id = "CRYPTO:BTC-USD:SPOT"
    query = MarketDataQuery(
        instrument_id=instrument_id,
        data_type=MarketDataType.QUOTE,
        as_of=AS_OF,
        venue="COINBASE",
    )
    future_quote = MarketQuote(
        instrument_id=instrument_id,
        currency="USD",
        bid=100_000,
        ask=100_001,
        provenance=provenance(
            venue="COINBASE",
            observed_at=AS_OF + timedelta(seconds=1),
        ),
    )

    with pytest.raises(ValueError, match="not available"):
        MarketDataBatch(query=query, records=(future_quote,))


def test_batch_rejects_cross_venue_conflation() -> None:
    instrument_id = "CRYPTO:BTC-USD:SPOT"
    query = MarketDataQuery(
        instrument_id=instrument_id,
        data_type=MarketDataType.QUOTE,
        as_of=AS_OF,
        venue="COINBASE",
    )
    quote = MarketQuote(
        instrument_id=instrument_id,
        currency="USD",
        bid=100_000,
        ask=100_001,
        provenance=provenance(venue="KRAKEN"),
    )

    with pytest.raises(ValueError, match="venue"):
        MarketDataBatch(query=query, records=(quote,))


def test_bar_query_requires_interval() -> None:
    with pytest.raises(ValueError, match="require an interval"):
        MarketDataQuery(
            instrument_id="CRYPTO:BTC-USD:SPOT",
            data_type=MarketDataType.BAR,
            as_of=AS_OF,
        )


def test_price_bar_rejects_invalid_ohlc_relationship() -> None:
    with pytest.raises(ValueError, match="greatest"):
        PriceBar(
            instrument_id="CRYPTO:BTC-USD:SPOT",
            currency="USD",
            interval=BarInterval.HOUR,
            start_at=AS_OF - timedelta(hours=1),
            end_at=AS_OF,
            open=100,
            high=99,
            low=95,
            close=98,
            volume=10,
            provenance=provenance(venue="COINBASE"),
        )


def test_announced_corporate_action_may_be_effective_later() -> None:
    instrument_id = (
        "SEC:CIK:0000320193:LISTING:NASDAQ:AAPL"
    )
    action = CorporateAction(
        instrument_id=instrument_id,
        currency="USD",
        action_type=CorporateActionType.CASH_DIVIDEND,
        effective_at=AS_OF + timedelta(days=10),
        amount=0.25,
        provenance=provenance(),
    )
    query = MarketDataQuery(
        instrument_id=instrument_id,
        data_type=MarketDataType.CORPORATE_ACTION,
        as_of=AS_OF,
    )

    batch = MarketDataBatch(query=query, records=(action,))

    assert batch.records == (action,)
    assert action.effective_at > action.provenance.observed_at


class FixtureMarketProvider:
    """Protocol fixture returning an empty bounded result."""

    @property
    def name(self) -> str:
        return "FIXTURE"

    def fetch(self, query: MarketDataQuery) -> MarketDataBatch:
        return MarketDataBatch(query=query, records=())


def test_provider_protocol_is_runtime_checkable() -> None:
    assert isinstance(
        FixtureMarketProvider(),
        CanonicalMarketDataProvider,
    )
