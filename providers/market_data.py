"""Market data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    currency: str = "USD"


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """Return the latest quote for a symbol."""
        raise NotImplementedError
