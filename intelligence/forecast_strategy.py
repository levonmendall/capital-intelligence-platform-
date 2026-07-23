"""Interface implemented by economic forecasting strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod

from intelligence.forecast import EconomicForecast
from intelligence.state import EconomicState


class ForecastStrategy(ABC):
    """Contract for all economic forecast implementations."""

    @abstractmethod
    def forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        """Produce a probabilistic forecast from an economic state."""

        raise NotImplementedError
