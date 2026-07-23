"""
Economic state domain models.

The Economic State represents the AI's best assessment of the current
economy based on normalized observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Strength(str, Enum):
    """Represents the strength of an economic component."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class Direction(str, Enum):
    """Represents the directional trend of an indicator."""

    IMPROVING = "improving"
    STABLE = "stable"
    DETERIORATING = "deteriorating"


@dataclass(frozen=True)
class EconomicState:
    """
    Canonical representation of the current economy.
    """

    growth: Strength
    inflation: Direction
    labor_market: Strength
    credit: Direction
    liquidity: Direction
    manufacturing: Direction
    housing: Direction
    consumer: Strength

    confidence: float

    summary: str

    def __post_init__(self) -> None:

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.summary.strip():
            raise ValueError(
                "summary cannot be empty"
            )
