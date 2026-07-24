"""Tests for canonical multi-asset identity contracts."""

from datetime import datetime, timezone

import pytest

from data import (
    AssetClass,
    IdentifierScheme,
    Instrument,
    InstrumentIdentifier,
    InstrumentType,
    Issuer,
    SecurityMasterError,
    SecurityMasterSnapshot,
    TradingCalendar,
    VenueListing,
    normalize_cik,
)


def equity_identity() -> tuple[Issuer, Instrument, VenueListing]:
    """Return one SEC-backed equity identity."""

    cik = normalize_cik(320193)
    issuer_id = f"SEC:CIK:{cik}"
    instrument_id = f"{issuer_id}:LISTING:NASDAQ:AAPL"
    issuer = Issuer(
        issuer_id=issuer_id,
        name="Apple Inc.",
        identifiers=(
            InstrumentIdentifier(
                IdentifierScheme.CIK,
                cik,
                provider="SEC_EDGAR",
            ),
        ),
    )
    instrument = Instrument(
        instrument_id=instrument_id,
        name="Apple Inc.",
        asset_class=AssetClass.EQUITY,
        instrument_type=InstrumentType.COMMON_STOCK,
        issuer_id=issuer_id,
        identifiers=(
            InstrumentIdentifier(
                IdentifierScheme.TICKER,
                "aapl",
                provider="SEC_EDGAR",
            ),
        ),
    )
    listing = VenueListing(
        instrument_id=instrument_id,
        venue="nasdaq",
        symbol="aapl",
        trading_calendar=TradingCalendar.EXCHANGE,
    )
    return issuer, instrument, listing


def test_cik_is_canonical_and_separate_from_instrument() -> None:
    issuer, instrument, listing = equity_identity()

    assert normalize_cik("320193") == "0000320193"
    assert issuer.issuer_id == "SEC:CIK:0000320193"
    assert instrument.issuer_id == issuer.issuer_id
    assert listing.symbol == "AAPL"
    assert listing.venue == "NASDAQ"


def test_crypto_spot_and_perpetual_require_no_sec_identity() -> None:
    spot = Instrument(
        instrument_id="CRYPTO:BTC-USD:SPOT",
        name="Bitcoin / U.S. Dollar",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.SPOT,
        base_asset="btc",
        quote_currency="usd",
    )
    perpetual = Instrument(
        instrument_id="CRYPTO:BTC-USDT:PERPETUAL",
        name="Bitcoin / Tether Perpetual",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.PERPETUAL,
        base_asset="btc",
        quote_currency="usdt",
        settlement_currency="usdt",
    )

    assert spot.issuer_id is None
    assert spot.base_asset == "BTC"
    assert perpetual.instrument_type is InstrumentType.PERPETUAL


def test_token_contract_address_is_network_scoped() -> None:
    token = Instrument(
        instrument_id="CRYPTO:ETHEREUM:USDC",
        name="USD Coin",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.STABLECOIN,
        network="ethereum",
        identifiers=(
            InstrumentIdentifier(
                IdentifierScheme.CONTRACT_ADDRESS,
                "0xa0b8",
                provider="onchain_registry",
            ),
        ),
    )

    assert token.network == "ethereum"
    assert token.identifiers[0].value == "0xa0b8"


def test_snapshot_resolves_venue_specific_symbols() -> None:
    issuer, equity, equity_listing = equity_identity()
    crypto = Instrument(
        instrument_id="CRYPTO:BTC-USD:SPOT",
        name="Bitcoin / U.S. Dollar",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.SPOT,
        base_asset="BTC",
        quote_currency="USD",
    )
    timestamp = datetime(2025, 2, 3, tzinfo=timezone.utc)
    snapshot = SecurityMasterSnapshot(
        observed_at=timestamp,
        retrieved_at=timestamp,
        issuers=(issuer,),
        instruments=(equity, crypto),
        listings=(
            equity_listing,
            VenueListing(
                instrument_id=crypto.instrument_id,
                venue="coinbase",
                symbol="BTC-USD",
                trading_calendar=TradingCalendar.CONTINUOUS,
            ),
        ),
        source="COMPOSITE_FIXTURE",
    )

    assert snapshot.resolve_symbol("aapl").instrument_id == (
        equity.instrument_id
    )
    assert snapshot.resolve_symbol(
        "btc-usd",
        venue="coinbase",
    ).asset_class is AssetClass.CRYPTO
    assert snapshot.instruments_for_issuer(
        issuer.issuer_id
    ) == (equity,)


def test_snapshot_requires_venue_for_ambiguous_symbol() -> None:
    first = Instrument(
        instrument_id="CRYPTO:VENUE_A:BTCUSD",
        name="Bitcoin / U.S. Dollar",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.SPOT,
        base_asset="BTC",
        quote_currency="USD",
    )
    second = Instrument(
        instrument_id="CRYPTO:VENUE_B:BTCUSD",
        name="Bitcoin / U.S. Dollar",
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.SPOT,
        base_asset="BTC",
        quote_currency="USD",
    )
    timestamp = datetime(2025, 2, 3, tzinfo=timezone.utc)
    snapshot = SecurityMasterSnapshot(
        observed_at=timestamp,
        retrieved_at=timestamp,
        issuers=(),
        instruments=(first, second),
        listings=(
            VenueListing(
                first.instrument_id,
                "VENUE_A",
                "BTCUSD",
                TradingCalendar.CONTINUOUS,
            ),
            VenueListing(
                second.instrument_id,
                "VENUE_B",
                "BTCUSD",
                TradingCalendar.CONTINUOUS,
            ),
        ),
        source="FIXTURE",
    )

    with pytest.raises(SecurityMasterError, match="specify a venue"):
        snapshot.resolve_symbol("BTCUSD")

    assert snapshot.resolve_symbol(
        "BTCUSD",
        venue="VENUE_B",
    ) == second


def test_instrument_rejects_incomplete_trading_pair() -> None:
    with pytest.raises(
        ValueError,
        match="base_asset and quote_currency",
    ):
        Instrument(
            instrument_id="CRYPTO:BTC:SPOT",
            name="Incomplete Bitcoin Pair",
            asset_class=AssetClass.CRYPTO,
            instrument_type=InstrumentType.SPOT,
            base_asset="BTC",
        )
