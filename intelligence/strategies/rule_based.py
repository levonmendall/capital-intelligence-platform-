"""Initial deterministic economic forecast strategy."""

from __future__ import annotations

from intelligence.forecast import (
    EconomicForecast,
    EconomicScenario,
    ScenarioForecast,
)
from intelligence.forecast_strategy import ForecastStrategy
from intelligence.state import (
    Direction,
    EconomicState,
    Strength,
)


class RuleBasedForecastStrategy(ForecastStrategy):
    """
    Produce scenario probabilities using transparent economic rules.

    This is the first forecast implementation. More advanced Bayesian,
    machine-learning, and ensemble strategies can later implement the
    same ForecastStrategy interface.
    """

    def __init__(
        self,
        horizon_months: int = 12,
    ) -> None:
        if horizon_months < 1:
            raise ValueError(
                "horizon_months must be at least 1"
            )

        self.horizon_months = horizon_months

    def forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        """Create a forecast based on the current economic state."""

        if self._supports_soft_landing(state):
            return self._soft_landing_forecast(state)

        if self._signals_recession(state):
            return self._recession_forecast(state)

        if self._signals_reacceleration(state):
            return self._reacceleration_forecast(state)

        if self._signals_stagflation(state):
            return self._stagflation_forecast(state)

        return self._uncertain_forecast(state)

    def _supports_soft_landing(
        self,
        state: EconomicState,
    ) -> bool:
        return (
            state.growth in {
                Strength.STRONG,
                Strength.MODERATE,
            }
            and state.inflation == Direction.IMPROVING
            and state.labor_market in {
                Strength.STRONG,
                Strength.MODERATE,
            }
            and state.credit != Direction.DETERIORATING
        )

    def _signals_recession(
        self,
        state: EconomicState,
    ) -> bool:
        weak_components = sum(
            (
                state.growth == Strength.WEAK,
                state.labor_market == Strength.WEAK,
                state.consumer == Strength.WEAK,
                state.credit == Direction.DETERIORATING,
                state.manufacturing == Direction.DETERIORATING,
            )
        )

        return weak_components >= 3

    def _signals_reacceleration(
        self,
        state: EconomicState,
    ) -> bool:
        return (
            state.growth == Strength.STRONG
            and state.labor_market == Strength.STRONG
            and state.consumer == Strength.STRONG
            and state.manufacturing
            == Direction.IMPROVING
            and state.inflation
            != Direction.DETERIORATING
        )

    def _signals_stagflation(
        self,
        state: EconomicState,
    ) -> bool:
        return (
            state.inflation == Direction.DETERIORATING
            and (
                state.growth == Strength.WEAK
                or state.manufacturing
                == Direction.DETERIORATING
            )
        )

    def _soft_landing_forecast(
       
