from intelligence.forecast import (
    EconomicForecast,
    ScenarioForecast,
    EconomicScenario,
)

from intelligence.state import (
    EconomicState,
    Strength,
    Direction,
)

from intelligence.forecast_strategy import (
    ForecastStrategy,
)


class RuleBasedForecastStrategy(
    ForecastStrategy
):

    """
    Initial deterministic forecasting model.

    Will later be replaced by more
    sophisticated probabilistic models.
    """

    def forecast(

        self,

        state: EconomicState,

    ) -> EconomicForecast:

        if (

            state.growth == Strength.MODERATE

            and

            state.inflation == Direction.IMPROVING

        ):

            scenarios = [

                ScenarioForecast(
                    EconomicScenario.SOFT_LANDING,
                    .60,
                    "Growth slowing while inflation cools.",
                ),

                ScenarioForecast(
                    EconomicScenario.RECESSION,
                    .20,
                    "Policy remains restrictive.",
                ),

                ScenarioForecast(
                    EconomicScenario.REACCELERATION,
                    .15,
                    "Demand unexpectedly rebounds.",
                ),

                ScenarioForecast(
                    EconomicScenario.STAGFLATION,
                    .05,
                    "Inflation returns.",
                ),
            ]

            confidence = .75

        else:

            scenarios = [

                ScenarioForecast(
                    EconomicScenario.SOFT_LANDING,
                    .25,
                    "Base case uncertain.",
                ),

                ScenarioForecast(
                    EconomicScenario.RECESSION,
                    .35,
                    "Weak growth dominates.",
                ),

                ScenarioForecast(
                    EconomicScenario.REACCELERATION,
                    .20,
                    "Upside surprise possible.",
                ),

                ScenarioForecast(
                    EconomicScenario.STAGFLATION,
                    .20,
                    "Inflation risk remains.",
                ),
            ]

            confidence = .55

        return EconomicForecast(

            current_state=state,

            scenarios=scenarios,

            confidence=confidence,

            summary=(

                f"Base case is "

                f"{max(scenarios, key=lambda s: s.probability).scenario.value}."

            ),
        )
