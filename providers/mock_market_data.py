"""Mock market data provider."""

from providers.market_data import (
    MarketDataProvider,
    Quote,
)


class MockMarketDataProvider(MarketDataProvider):

    _prices = {
        "SPY": 650.25,
        "QQQ": 598.74,
        "VTI": 335.18,
        "IWM": 246.92,
        "AGG": 98.51,
        "BND": 71.34,
        "GLD": 348.22,
        "VNQ": 92.81,
        "SGOV": 100.03,
    }

    def get_quote(self, symbol: str) -> Quote:

        return Quote(
            symbol=symbol,
            price=self._prices[symbol],
        )
