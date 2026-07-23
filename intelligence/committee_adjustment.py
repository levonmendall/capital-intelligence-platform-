"""
Committee confidence adjustment domain models.

Committee members propose score adjustments during their analysis.
The AdjustmentEngine determines how much of each proposed adjustment
may be applied under the active adjustment policy.

Keeping raw and applied values preserves a complete audit trail.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterator, overload


class AdjustmentCategory(str, Enum):
    """Classification of committee confidence adjustments."""

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
    One auditable confidence adjustment.

    Parameters
    ----------
    category:
        Analytical category responsible for the adjustment.

    description:
        Human-readable explanation of the adjustment.

    raw_value:
        Adjustment proposed by the committee member.

    applied_value:
        Adjustment permitted by the AdjustmentEngine. When omitted,
        it initially equals raw_value.

    constraint_reason:
        Explanation of why applied_value differs from raw_value.
    """

    category: AdjustmentCategory
    description: str
    raw_value: float
    applied_value: float | None = None
    constraint_reason: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize the adjustment."""

        if not isinstance(self.category, AdjustmentCategory):
            raise TypeError(
                "category must be an AdjustmentCategory."
            )

        if not isinstance(self.description, str):
            raise TypeError(
                "description must be a string."
            )

        description = self.description.strip()

        if not description:
            raise ValueError(
                "description cannot be empty."
            )

        if not isinstance(self.raw_value, (int, float)):
            raise TypeError(
                "raw_value must be numeric."
            )

        raw_value = float(self.raw_value)

        if not isfinite(raw_value):
            raise ValueError(
                "raw_value must be finite."
            )

        if not -1.0 <= raw_value <= 1.0:
            raise ValueError(
                "raw_value must be between -1.0 and 1.0."
            )

        applied_value = (
            raw_value
            if self.applied_value is None
            else float(self.applied_value)
        )

        if not isfinite(applied_value):
            raise ValueError(
                "applied_value must be finite."
            )

        if not -1.0 <= applied_value <= 1.0:
            raise ValueError(
                "applied_value must be between -1.0 and 1.0."
            )

        if not isinstance(self.constraint_reason, str):
            raise TypeError(
                "constraint_reason must be a string."
            )

        object.__setattr__(
            self,
            "description",
            description,
        )

        object.__setattr__(
            self,
            "raw_value",
            round(raw_value, 4),
        )

        object.__setattr__(
            self,
            "applied_value",
            round(applied_value, 4),
        )

        object.__setattr__(
            self,
            "constraint_reason",
            self.constraint_reason.strip(),
        )

    @property
    def value(self) -> float:
        """
        Backward-compatible alias for applied_value.
        """

        return float(self.applied_value)

    @property
    def was_constrained(self) -> bool:
        """Whether policy changed the proposed adjustment."""

        return self.raw_value != self.applied_value

    @property
    def is_positive(self) -> bool:
        """Whether the applied adjustment increases confidence."""

        return self.value > 0.0

    @property
    def is_negative(self) -> bool:
        """Whether the applied adjustment decreases confidence."""

        return self.value < 0.0

    @property
    def is_neutral(self) -> bool:
        """Whether the applied adjustment has no effect."""

        return self.value == 0.0

    def with_applied_value(
        self,
        applied_value: float,
        *,
        constraint_reason: str = "",
    ) -> ScoreAdjustment:
        """
        Return a new adjustment containing the policy-approved value.
        """

        return ScoreAdjustment(
            category=self.category,
            description=self.description,
            raw_value=self.raw_value,
            applied_value=applied_value,
            constraint_reason=constraint_reason,
        )


@dataclass(frozen=True, slots=True)
class AdjustmentSet:
    """
    Immutable collection of score adjustments.
    """

    adjustments: tuple[ScoreAdjustment, ...] = ()

    def __post_init__(self) -> None:
        """Validate collection members."""

        if not isinstance(self.adjustments, tuple):
            raise TypeError(
                "adjustments must be a tuple."
            )

        for adjustment in self.adjustments:
            if not isinstance(
                adjustment,
                ScoreAdjustment,
            ):
                raise TypeError(
                    "adjustments must contain only "
                    "ScoreAdjustment objects."
                )

    def __iter__(self) -> Iterator[ScoreAdjustment]:
        return iter(self.adjustments)

    def __len__(self) -> int:
        return len(self.adjustments)

    def __bool__(self) -> bool:
        return bool(self.adjustments)

    @overload
    def __getitem__(
        self,
        index: int,
    ) -> ScoreAdjustment:
        ...

    @overload
    def __getitem__(
        self,
        index: slice,
    ) -> tuple[ScoreAdjustment, ...]:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> ScoreAdjustment | tuple[ScoreAdjustment, ...]:
        return self.adjustments[index]

    @property
    def total_raw_adjustment(self) -> float:
        """Sum of proposed adjustments."""

        return round(
            sum(
                adjustment.raw_value
                for adjustment in self.adjustments
            ),
            4,
        )

    @property
    def total_applied_adjustment(self) -> float:
        """Sum of policy-approved adjustments."""

        return round(
            sum(
                adjustment.value
                for adjustment in self.adjustments
            ),
            4,
        )

    @property
    def total_adjustment(self) -> float:
        """
        Backward-compatible alias for total_applied_adjustment.
        """

        return self.total_applied_adjustment

    @property
    def positives(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """Applied positive adjustments."""

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_positive
        )

    @property
    def negatives(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """Applied negative adjustments."""

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_negative
        )

    @property
    def neutrals(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """Applied neutral adjustments."""

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_neutral
        )

    @property
    def constrained(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """Adjustments modified by policy."""

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.was_constrained
        )

    @property
    def categories(
        self,
    ) -> tuple[AdjustmentCategory, ...]:
        """Categories represented in the set."""

        return tuple(
            sorted(
                {
                    adjustment.category
                    for adjustment in self.adjustments
                },
                key=lambda category: category.value,
            )
        )

    def by_category(
        self,
        category: AdjustmentCategory,
    ) -> tuple[ScoreAdjustment, ...]:
        """Return adjustments belonging to one category."""

        if not isinstance(
            category,
            AdjustmentCategory,
        ):
            raise TypeError(
                "category must be an AdjustmentCategory."
            )

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.category == category
        )

    def summary(self) -> str:
        """Produce an auditable adjustment summary."""

        if not self.adjustments:
            return "No score adjustments."

        lines: list[str] = []

        for adjustment in self.adjustments:
            applied_sign = (
                "+"
                if adjustment.value >= 0.0
                else ""
            )

            line = (
                f"{applied_sign}{adjustment.value:.2f} | "
                f"{adjustment.category.value:<10} | "
                f"{adjustment.description}"
            )

            if adjustment.was_constrained:
                raw_sign = (
                    "+"
                    if adjustment.raw_value >= 0.0
                    else ""
                )

                line += (
                    f" | proposed "
                    f"{raw_sign}{adjustment.raw_value:.2f}"
                )

                if adjustment.constraint_reason:
                    line += (
                        f" | {adjustment.constraint_reason}"
                    )

            lines.append(line)

        lines.extend(
            [
                "",
                (
                    "Raw Adjustment: "
                    f"{self.total_raw_adjustment:+.2f}"
                ),
                (
                    "Applied Adjustment: "
                    f"{self.total_applied_adjustment:+.2f}"
                ),
            ]
        )

        return "\n".join(lines)
