"""Provider-neutral point-in-time contracts for multi-asset market data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Protocol, TypeAlias, runtime_checkable

from data.observation import DataQualityState
from data.provider import ProviderError


class MarketDataError(ProviderError):
    """Base error for unavailable or invalid market data."""


class MarketDataType(str, Enum):
    """Canonical market-data record categories."""

    QUOTE = "quote"
    TRADE = "trade"
    BAR = "bar"
    CORPORATE_ACTION = "corporate_action"
    FUNDING_RATE = "funding_rate"
    OPEN_INTEREST = "open_interest"


class BarInterval(str, Enum):
    """Supported aggregation intervals."""

    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    HOUR = "1h"
    DAY = "1d"


class TradeSide(str, Enum):
    """Provider-reported aggressor side when available."""

    BUY = "buy"
    SELL = "sell"
    UNKNOWN = "unknown"


class CorporateActionType(str, Enum):
    """Canonical issuer or instrument action."""

    CASH_DIVIDEND = "cash_dividend"
    STOCK_DIVIDEND = "stock_dividend"
    SPLIT = "split"
    REVERSE_SPLIT = "reverse_split"
    SYMBOL_CHANGE = "symbol_change"
    MERGER = "merger"
    SPINOFF = "spinoff"
    DELISTING = "delisting"
    OTHER = "other"


def _required_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _optional_text(
    value: object,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return _required_text(value, field_name=field_name)


def _aware_datetime(value: object, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _number(
    value: object,
    *,
    field_name: str,
    minimum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{field_name} must be finite")
    if minimum is not None and normalized < minimum:
        raise ValueError(
            f"{field_name} must be greater than or equal to {minimum}"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class MarketDataProvenance:
    """Provider, venue, and availability metadata for a market record."""

    provider: str
    venue: str
    observed_at: datetime
    retrieved_at: datetime
    quality_state: DataQualityState
    provider_record_id: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("provider", "venue"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ).upper(),
            )
        observed_at = _aware_datetime(
            self.observed_at,
            field_name="observed_at",
        )
        retrieved_at = _aware_datetime(
            self.retrieved_at,
            field_name="retrieved_at",
        )
        if observed_at > retrieved_at:
            raise ValueError(
                "observed_at cannot be later than retrieved_at"
            )
        if not isinstance(self.quality_state, DataQualityState):
            raise TypeError(
                "quality_state must be a DataQualityState"
            )
        object.__setattr__(
            self,
            "provider_record_id",
            _optional_text(
                self.provider_record_id,
                field_name="provider_record_id",
            ),
        )


@dataclass(frozen=True, slots=True)
class MarketDataQuery:
    """Bounded point-in-time request for one instrument and venue."""

    instrument_id: str
    data_type: MarketDataType
    as_of: datetime
    start_at: datetime | None = None
    venue: str | None = None
    interval: BarInterval | None = None
    limit: int = 500

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "instrument_id",
            _required_text(
                self.instrument_id,
                field_name="instrument_id",
            ),
        )
        if not isinstance(self.data_type, MarketDataType):
            raise TypeError(
                "data_type must be a MarketDataType"
            )
        as_of = _aware_datetime(self.as_of, field_name="as_of")
        if self.start_at is not None:
            start_at = _aware_datetime(
                self.start_at,
                field_name="start_at",
            )
            if start_at > as_of:
                raise ValueError(
                    "start_at cannot be later than as_of"
                )
        object.__setattr__(
            self,
            "venue",
            (
                _required_text(self.venue, field_name="venue").upper()
                if self.venue is not None
                else None
            ),
        )
        if self.interval is not None and not isinstance(
            self.interval,
            BarInterval,
        ):
            raise TypeError(
                "interval must be a BarInterval or None"
            )
        if self.data_type is MarketDataType.BAR:
            if self.interval is None:
                raise ValueError("bar queries require an interval")
        elif self.interval is not None:
            raise ValueError(
                "interval is only valid for bar queries"
            )
        if isinstance(self.limit, bool) or not isinstance(
            self.limit,
            int,
        ):
            raise TypeError("limit must be an int")
        if not 1 <= self.limit <= 100_000:
            raise ValueError(
                "limit must be between 1 and 100000"
            )


@dataclass(frozen=True, slots=True)
class MarketQuote:
    """One bid, ask, and optional last-price snapshot."""

    instrument_id: str
    currency: str
    bid: float
    ask: float
    provenance: MarketDataProvenance
    last: float | None = None
    bid_size: float | None = None
    ask_size: float | None = None

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        bid = _number(self.bid, field_name="bid")
        ask = _number(self.ask, field_name="ask")
        if bid > ask:
            raise ValueError("bid cannot be greater than ask")
        object.__setattr__(self, "bid", bid)
        object.__setattr__(self, "ask", ask)
        for field_name in ("last", "bid_size", "ask_size"):
            value = getattr(self, field_name)
            if value is not None:
                minimum = 0.0 if field_name.endswith("size") else None
                object.__setattr__(
                    self,
                    field_name,
                    _number(
                        value,
                        field_name=field_name,
                        minimum=minimum,
                    ),
                )


@dataclass(frozen=True, slots=True)
class MarketTrade:
    """One provider-reported market trade."""

    instrument_id: str
    currency: str
    price: float
    size: float
    side: TradeSide
    provenance: MarketDataProvenance

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        object.__setattr__(
            self,
            "price",
            _number(self.price, field_name="price"),
        )
        object.__setattr__(
            self,
            "size",
            _number(self.size, field_name="size", minimum=0.0),
        )
        if not isinstance(self.side, TradeSide):
            raise TypeError("side must be a TradeSide")


@dataclass(frozen=True, slots=True)
class PriceBar:
    """One OHLCV interval with explicit temporal boundaries."""

    instrument_id: str
    currency: str
    interval: BarInterval
    start_at: datetime
    end_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    provenance: MarketDataProvenance

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        if not isinstance(self.interval, BarInterval):
            raise TypeError("interval must be a BarInterval")
        start_at = _aware_datetime(
            self.start_at,
            field_name="start_at",
        )
        end_at = _aware_datetime(self.end_at, field_name="end_at")
        if start_at >= end_at:
            raise ValueError("start_at must be earlier than end_at")
        if end_at > self.provenance.observed_at:
            raise ValueError(
                "bar end cannot be later than observed_at"
            )
        prices = {
            field_name: _number(
                getattr(self, field_name),
                field_name=field_name,
            )
            for field_name in ("open", "high", "low", "close")
        }
        if prices["high"] < max(
            prices["open"],
            prices["low"],
            prices["close"],
        ):
            raise ValueError(
                "high must be the greatest bar price"
            )
        if prices["low"] > min(
            prices["open"],
            prices["high"],
            prices["close"],
        ):
            raise ValueError("low must be the least bar price")
        for field_name, value in prices.items():
            object.__setattr__(self, field_name, value)
        object.__setattr__(
            self,
            "volume",
            _number(
                self.volume,
                field_name="volume",
                minimum=0.0,
            ),
        )


@dataclass(frozen=True, slots=True)
class FundingRate:
    """One perpetual-contract funding interval."""

    instrument_id: str
    currency: str
    period_start: datetime
    period_end: datetime
    rate: float
    provenance: MarketDataProvenance

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        period_start = _aware_datetime(
            self.period_start,
            field_name="period_start",
        )
        period_end = _aware_datetime(
            self.period_end,
            field_name="period_end",
        )
        if period_start >= period_end:
            raise ValueError(
                "period_start must be earlier than period_end"
            )
        if period_end > self.provenance.observed_at:
            raise ValueError(
                "funding period cannot end after observed_at"
            )
        object.__setattr__(
            self,
            "rate",
            _number(self.rate, field_name="rate"),
        )


@dataclass(frozen=True, slots=True)
class OpenInterest:
    """One venue-specific derivative open-interest observation."""

    instrument_id: str
    currency: str
    value: float
    provenance: MarketDataProvenance

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        object.__setattr__(
            self,
            "value",
            _number(
                self.value,
                field_name="value",
                minimum=0.0,
            ),
        )


@dataclass(frozen=True, slots=True)
class CorporateAction:
    """One announced corporate action without adjusted-price mutation."""

    instrument_id: str
    currency: str
    action_type: CorporateActionType
    effective_at: datetime
    provenance: MarketDataProvenance
    amount: float | None = None
    ratio: float | None = None
    new_symbol: str | None = None

    def __post_init__(self) -> None:
        _normalize_record_identity(self)
        if not isinstance(self.action_type, CorporateActionType):
            raise TypeError(
                "action_type must be a CorporateActionType"
            )
        _aware_datetime(
            self.effective_at,
            field_name="effective_at",
        )
        for field_name in ("amount", "ratio"):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _number(
                        value,
                        field_name=field_name,
                        minimum=0.0,
                    ),
                )
        object.__setattr__(
            self,
            "new_symbol",
            (
                _required_text(
                    self.new_symbol,
                    field_name="new_symbol",
                ).upper()
                if self.new_symbol is not None
                else None
            ),
        )


MarketDataRecord: TypeAlias = (
    MarketQuote
    | MarketTrade
    | PriceBar
    | FundingRate
    | OpenInterest
    | CorporateAction
)


@dataclass(frozen=True, slots=True)
class MarketDataBatch:
    """Typed result for one canonical market-data query."""

    query: MarketDataQuery
    records: tuple[MarketDataRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.query, MarketDataQuery):
            raise TypeError("query must be a MarketDataQuery")
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        expected_type = {
            MarketDataType.QUOTE: MarketQuote,
            MarketDataType.TRADE: MarketTrade,
            MarketDataType.BAR: PriceBar,
            MarketDataType.CORPORATE_ACTION: CorporateAction,
            MarketDataType.FUNDING_RATE: FundingRate,
            MarketDataType.OPEN_INTEREST: OpenInterest,
        }[self.query.data_type]
        if not all(
            isinstance(record, expected_type)
            for record in self.records
        ):
            raise TypeError(
                "records do not match the query data_type"
            )
        for record in self.records:
            if record.instrument_id != self.query.instrument_id:
                raise ValueError(
                    "record instrument does not match query"
                )
            if (
                record.provenance.observed_at > self.query.as_of
            ):
                raise ValueError(
                    "record was not available at query as_of"
                )
            if (
                self.query.start_at is not None
                and record.provenance.observed_at
                < self.query.start_at
            ):
                raise ValueError(
                    "record is earlier than query start_at"
                )
            if (
                self.query.venue is not None
                and record.provenance.venue != self.query.venue
            ):
                raise ValueError(
                    "record venue does not match query"
                )
        if len(self.records) > self.query.limit:
            raise ValueError("records exceed query limit")


@runtime_checkable
class CanonicalMarketDataProvider(Protocol):
    """Provider capable of canonical point-in-time market retrieval."""

    @property
    def name(self) -> str:
        """Stable provider identifier."""

    def fetch(self, query: MarketDataQuery) -> MarketDataBatch:
        """Return market records available at the query boundary."""


def _normalize_record_identity(record: object) -> None:
    object.__setattr__(
        record,
        "instrument_id",
        _required_text(
            getattr(record, "instrument_id"),
            field_name="instrument_id",
        ),
    )
    object.__setattr__(
        record,
        "currency",
        _required_text(
            getattr(record, "currency"),
            field_name="currency",
        ).upper(),
    )
    provenance = getattr(record, "provenance")
    if not isinstance(provenance, MarketDataProvenance):
        raise TypeError(
            "provenance must be MarketDataProvenance"
        )
