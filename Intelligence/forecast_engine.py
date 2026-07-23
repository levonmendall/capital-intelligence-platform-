from intelligence.forecast_strategy import (
    ForecastStrategy,
)

from intelligence.forecast import EconomicForecast

from intelligence.state import EconomicState


class ForecastEngine:

    """
    Delegates forecasting to the configured strategy.
    """

    def __init__(

        self,

        strategy: ForecastStrategy,

    ):

        self.strategy = strategy

    def forecast(

        self,

        state: EconomicState,

    ) -> EconomicForecast:

        return self.strategy.forecast(state)
