"""Initial transparent, rule-based economic forecast strategy."""

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

    This initial implementation is deterministic and explainable.
    Future Bayesian, machine-learning, or ensemble strategies can
    implement the same ForecastStrategy interface.
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
        """Create a forecast from the current economic state."""

        if not isinstance(state, EconomicState):
            raise TypeError(
                "state must be an EconomicState"
            )

        if self._signals_recession(state):
            return self._recession_forecast(state)

        if self._signals_stagflation(state):
            return self._stagflation_forecast(state)

        if self._signals_reacceleration(state):
            return self._reacceleration_forecast(state)

        if self._supports_soft_landing(state):
            return self._soft_landing_forecast(state)

        return self._uncertain_forecast(state)

    def _supports_soft_landing(
        self,
        state: EconomicState,
    ) -> bool:
        return (
            state.growth
            in {
                Strength.STRONG,
                Strength.MODERATE,
            }
            and state.inflation == Direction.IMPROVING
            and state.labor_market
            in {
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
                state.manufacturing
                == Direction.DETERIORATING,
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
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        scenarios = (
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=0.60,
                rationale=(
                    "Growth remains positive while inflation "
                    "improves and labor conditions remain resilient."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=0.20,
                rationale=(
                    "Restrictive financial conditions could weaken "
                    "growth more sharply than expected."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=0.15,
                rationale=(
                    "Strong demand and labor conditions could cause "
                    "economic activity to accelerate."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=0.05,
                rationale=(
                    "A renewed inflation shock remains possible but "
                    "is not currently the dominant outcome."
                ),
            ),
        )

        return self._build_forecast(
            state=state,
            scenarios=scenarios,
            confidence=0.75,
            summary=(
                "The base case is a soft landing, supported by "
                "positive growth, improving inflation, and resilient "
                "labor conditions."
            ),
        )

    def _recession_forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        scenarios = (
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=0.20,
                rationale=(
                    "Economic weakness may stabilize before becoming "
                    "a full recession."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=0.55,
                rationale=(
                    "Multiple growth-sensitive components are weak "
                    "or deteriorating."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=0.10,
                rationale=(
                    "A rapid improvement in demand or policy support "
                    "could revive growth."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=0.15,
                rationale=(
                    "Weak growth could coexist with persistent or "
                    "renewed inflation."
                ),
            ),
        )

        return self._build_forecast(
            state=state,
            scenarios=scenarios,
            confidence=0.72,
            summary=(
                "The base case is recession because several "
                "growth-sensitive economic components are weak or "
                "deteriorating."
            ),
        )

    def _reacceleration_forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        scenarios = (
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=0.25,
                rationale=(
                    "Growth may remain healthy without accelerating "
                    "materially."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=0.10,
                rationale=(
                    "A delayed response to restrictive conditions "
                    "could still weaken growth."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=0.55,
                rationale=(
                    "Strong growth, labor, consumer, and manufacturing "
                    "conditions support renewed acceleration."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=0.10,
                rationale=(
                    "Stronger demand could eventually revive inflation."
                ),
            ),
        )

        return self._build_forecast(
            state=state,
            scenarios=scenarios,
            confidence=0.74,
            summary=(
                "The base case is economic reacceleration, supported "
                "by broad strength in growth, labor, consumer demand, "
                "and manufacturing."
            ),
        )

    def _stagflation_forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        scenarios = (
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=0.15,
                rationale=(
                    "Inflation pressures may ease before causing "
                    "lasting damage to growth."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=0.25,
                rationale=(
                    "Weak growth could deepen if financial conditions "
                    "remain restrictive."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=0.10,
                rationale=(
                    "Demand could strengthen despite inflation risks."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=0.50,
                rationale=(
                    "Inflation is deteriorating while growth or "
                    "manufacturing conditions are weak."
                ),
            ),
        )

        return self._build_forecast(
            state=state,
            scenarios=scenarios,
            confidence=0.70,
            summary=(
                "The base case is stagflation because inflation is "
                "deteriorating while growth-sensitive conditions are "
                "weak."
            ),
        )

    def _uncertain_forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        scenarios = (
            ScenarioForecast(
                scenario=EconomicScenario.SOFT_LANDING,
                probability=0.35,
                rationale=(
                    "The economy may continue growing while inflation "
                    "gradually stabilizes."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.RECESSION,
                probability=0.25,
                rationale=(
                    "Mixed conditions leave meaningful downside risk."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.REACCELERATION,
                probability=0.20,
                rationale=(
                    "Demand or policy conditions could strengthen."
                ),
            ),
            ScenarioForecast(
                scenario=EconomicScenario.STAGFLATION,
                probability=0.20,
                rationale=(
                    "Inflation and growth signals remain sufficiently "
                    "mixed to preserve stagflation risk."
                ),
            ),
        )

        return self._build_forecast(
            state=state,
            scenarios=scenarios,
            confidence=0.55,
            summary=(
                "The outlook is mixed. A soft landing is the highest-"
                "probability scenario, but conviction is limited."
            ),
        )

    def _build_forecast(
        self,
        *,
        state: EconomicState,
        scenarios: tuple[ScenarioForecast, ...],
        confidence: float,
        summary: str,
    ) -> EconomicForecast:
        return EconomicForecast(
            current_state=state,
            scenarios=scenarios,
            confidence=confidence,
            summary=summary,
            horizon_months=self.horizon_months,
        )
