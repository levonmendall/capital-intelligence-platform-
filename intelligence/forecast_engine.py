"""Forecast-engine orchestration."""

from __future__ import annotations

from intelligence.forecast import EconomicForecast
from intelligence.forecast_strategy import ForecastStrategy
from intelligence.state import EconomicState


class ForecastEngine:
    """Runs the configured economic forecast strategy."""

    def __init__(
        self,
        strategy: ForecastStrategy,
    ) -> None:
        if not isinstance(strategy, ForecastStrategy):
            raise TypeError(
                "strategy must implement ForecastStrategy"
            )

        self._strategy = strategy

    @property
    def strategy(self) -> ForecastStrategy:
        """Return the currently configured forecast strategy."""

        return self._strategy

    def set_strategy(
        self,
        strategy: ForecastStrategy,
    ) -> None:
        """Replace the forecasting strategy at runtime."""

        if not isinstance(strategy, ForecastStrategy):
            raise TypeError(
                "strategy must implement ForecastStrategy"
            )

        self._strategy = strategy

    def forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        """Generate an economic forecast."""

        if not isinstance(state, EconomicState):
            raise TypeError(
                "state must be an EconomicState"
            )

        return self._strategy.forecast(state)
