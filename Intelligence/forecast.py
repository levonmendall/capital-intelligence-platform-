"""
Forecast domain models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from intelligence.state import EconomicState


class EconomicScenario(str, Enum):
    SOFT_LANDING = "soft_landing"
    RECESSION = "recession"
    REACCELERATION = "reacceleration"
    STAGFLATION = "stagflation"


@dataclass(frozen=True)
class ScenarioForecast:
    """
    Probability assigned to one future scenario.
    """

    scenario: EconomicScenario

    probability: float

    rationale: str

    def __post_init__(self):

        if not 0 <= self.probability <= 1:
            raise ValueError(
                "probability must be between 0 and 1"
            )


@dataclass(frozen=True)
class EconomicForecast:
    """
    Forward-looking macro forecast.
    """

    current_state: EconomicState

    scenarios: list[ScenarioForecast]

    confidence: float

    summary: str

    def __post_init__(self):

        total = sum(
            scenario.probability
            for scenario in self.scenarios
        )

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                "Scenario probabilities must equal 1."
            )

    @property
    def base_case(self):

        return max(
            self.scenarios,
            key=lambda s: s.probability,
        )
