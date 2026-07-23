"""Domain models for forward-looking economic forecasts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from intelligence.state import EconomicState


class EconomicScenario(str, Enum):
    """Economic scenarios supported by the initial forecast engine."""

    SOFT_LANDING = "soft_landing"
    RECESSION = "recession"
    REACCELERATION = "reacceleration"
    STAGFLATION = "stagflation"


@dataclass(frozen=True)
class ScenarioForecast:
    """Probability and rationale assigned to one economic scenario."""

    scenario: EconomicScenario
    probability: float
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(
                "probability must be between 0.0 and 1.0"
            )

        if not self.rationale.strip():
            raise ValueError("rationale cannot be empty")


@dataclass(frozen=True)
class EconomicForecast:
    """Complete probabilistic forecast for a future economic period."""

    current_state: EconomicState
    scenarios: tuple[ScenarioForecast, ...]
    confidence: float
    summary: str
    horizon_months: int = 12

    def __post_init__(self) -> None:
        if not self.scenarios:
            raise ValueError(
                "scenarios must contain at least one forecast"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

        if self.horizon_months < 1:
            raise ValueError(
                "horizon_months must be at least 1"
            )

        scenario_names = [
            forecast.scenario
            for forecast in self.scenarios
        ]

        if len(scenario_names) != len(set(scenario_names)):
            raise ValueError(
                "each economic scenario may appear only once"
            )

        probability_total = sum(
            forecast.probability
            for forecast in self.scenarios
        )

        if abs(probability_total - 1.0) > 0.001:
            raise ValueError(
                "scenario probabilities must total 1.0; "
                f"received {probability_total:.4f}"
            )

    @property
    def base_case(self) -> ScenarioForecast:
        """Return the scenario with the highest probability."""

        return max(
            self.scenarios,
            key=lambda forecast: forecast.probability,
        )

    def probability_for(
        self,
        scenario: EconomicScenario,
    ) -> float:
        """Return the probability assigned to a given scenario."""

        for forecast in self.scenarios:
            if forecast.scenario == scenario:
                return forecast.probability

        return 0.0
