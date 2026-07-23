"""
Committee scoring adjustments.

Committee members should explain every confidence adjustment
using standardized score adjustments.

These adjustments provide a complete audit trail describing
how a committee member arrived at its final confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AdjustmentCategory(str, Enum):
    """
    Classification of confidence adjustments.
    """

    ECONOMIC = "economic"

    ALLOCATION = "allocation"

    DURATION = "duration"

    RISK = "risk"

    VALUATION = "valuation"

    CREDIT = "credit"

    LIQUIDITY = "liquidity"

    TECHNICAL = "technical"

    POLICY = "policy"

    OTHER = "other"


@dataclass(frozen=True, slots=True)
class ScoreAdjustment:
    """
    One individual confidence adjustment.

    Positive values increase confidence.

    Negative values decrease confidence.
    """

    category: AdjustmentCategory

    description: str

    value: float

    def __post_init__(self) -> None:

        if not self.description.strip():
            raise ValueError(
                "description cannot be empty."
            )

        if not -1.0 <= self.value <= 1.0:
            raise ValueError(
                "value must be between -1.0 and 1.0."
            )

    @property
    def is_positive(self) -> bool:
        return self.value > 0.0

    @property
    def is_negative(self) -> bool:
        return self.value < 0.0

    @property
    def is_neutral(self) -> bool:
        return self.value == 0.0


class AdjustmentSet(tuple[ScoreAdjustment, ...]):
    """
    Immutable collection of score adjustments.
    """

    @property
    def total_adjustment(self) -> float:
        return round(
            sum(
                adjustment.value
                for adjustment in self
            ),
            4,
        )

    @property
    def positives(self) -> tuple[ScoreAdjustment, ...]:
        return tuple(
            adjustment
            for adjustment in self
            if adjustment.is_positive
        )

    @property
    def negatives(self) -> tuple[ScoreAdjustment, ...]:
        return tuple(
            adjustment
            for adjustment in self
            if adjustment.is_negative
        )

    @property
    def by_category(
        self,
    ) -> dict[AdjustmentCategory, tuple[ScoreAdjustment, ...]]:

        result: dict[
            AdjustmentCategory,
            list[ScoreAdjustment],
        ] = {}

        for adjustment in self:

            result.setdefault(
                adjustment.category,
                [],
            ).append(adjustment)

        return {
            key: tuple(value)
            for key, value in result.items()
        }

    def summary(self) -> str:

        if not self:
            return "No score adjustments."

        lines = []

        for adjustment in self:

            sign = "+" if adjustment.value >= 0 else ""

            lines.append(
                f"{sign}{adjustment.value:.2f} "
                f"{adjustment.category.value}: "
                f"{adjustment.description}"
            )

        lines.append("")
        lines.append(
            f"Total Adjustment: "
            f"{self.total_adjustment:+.2f}"
        )

        return "\n".join(lines)
