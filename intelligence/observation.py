"""Normalized economic observation models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ObservationCategory(str, Enum):
    """High-level economic observation categories."""

    GROWTH = "growth"
    INFLATION = "inflation"
    LABOR = "labor"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    MANUFACTURING = "manufacturing"
    HOUSING = "housing"
    CONSUMER = "consumer"


class Trend(str, Enum):
    """Direction of change in an economic indicator."""

    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"


class IndicatorId(str, Enum):
    """Canonical identifiers used by the initial state engine."""

    GDP = "gdp"
    CORE_CPI = "core_cpi"
    UNEMPLOYMENT = "unemployment"
    ISM_MANUFACTURING = "ism_manufacturing"


@dataclass(frozen=True)
class Observation:
    """One normalized economic data observation."""

    indicator: str
    category: ObservationCategory
    value: float
    previous_value: float | None = None
    trend: Trend = Trend.STABLE
    unit: str = ""
    source: str = ""
    importance: float = 1.0

    def __post_init__(self) -> None:
        if not self.indicator.strip():
            raise ValueError("indicator cannot be empty")

        if not 0.0 <= self.importance <= 1.0:
            raise ValueError(
                "importance must be between 0.0 and 1.0"
            )


@dataclass
class ObservationSet:
    """Collection of normalized economic observations."""

    observations: list[Observation] = field(default_factory=list)

    def add(self, observation: Observation) -> None:
        if not isinstance(observation, Observation):
            raise TypeError(
                "observation must be an Observation"
            )

        self.observations.append(observation)

    def indicator(
        self,
        indicator: str,
    ) -> Observation | None:
        """Return the most recently added matching observation."""

        for observation in reversed(self.observations):
            if observation.indicator == indicator:
                return observation

        return None

    def by_category(
        self,
        category: ObservationCategory,
    ) -> tuple[Observation, ...]:
        """Return all observations in a category."""

        return tuple(
            observation
            for observation in self.observations
            if observation.category == category
        )

    def __len__(self) -> int:
        return len(self.observations)
