@dataclass(frozen=True, slots=True)
class AdjustmentSet:
    """
    Immutable collection of score adjustments.

    This class provides aggregation, filtering, and reporting
    functionality while preserving immutability.
    """

    adjustments: tuple[ScoreAdjustment, ...]

    def __post_init__(self) -> None:

        for adjustment in self.adjustments:

            if not isinstance(
                adjustment,
                ScoreAdjustment,
            ):
                raise TypeError(
                    "adjustments must contain only "
                    "ScoreAdjustment objects."
                )

    def __iter__(self):
        return iter(self.adjustments)

    def __len__(self) -> int:
        return len(self.adjustments)

    def __getitem__(
        self,
        index: int,
    ) -> ScoreAdjustment:
        return self.adjustments[index]

    @property
    def total_adjustment(self) -> float:
        """
        Sum of every score adjustment.
        """

        return round(
            sum(
                adjustment.value
                for adjustment in self.adjustments
            ),
            4,
        )

    @property
    def positives(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """
        Positive score adjustments.
        """

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_positive
        )

    @property
    def negatives(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """
        Negative score adjustments.
        """

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_negative
        )

    @property
    def neutrals(
        self,
    ) -> tuple[ScoreAdjustment, ...]:
        """
        Neutral score adjustments.
        """

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.is_neutral
        )

    def by_category(
        self,
        category: AdjustmentCategory,
    ) -> tuple[ScoreAdjustment, ...]:
        """
        Return adjustments belonging to a single category.
        """

        return tuple(
            adjustment
            for adjustment in self.adjustments
            if adjustment.category == category
        )

    @property
    def categories(
        self,
    ) -> tuple[AdjustmentCategory, ...]:
        """
        Categories represented in this adjustment set.
        """

        return tuple(
            sorted(
                {
                    adjustment.category
                    for adjustment in self.adjustments
                },
                key=lambda category: category.value,
            )
        )

    def summary(self) -> str:
        """
        Produce a human-readable summary of every adjustment.
        """

        if not self.adjustments:
            return "No score adjustments."

        lines: list[str] = []

        for adjustment in self.adjustments:

            sign = "+" if adjustment.value >= 0 else ""

            lines.append(
                f"{sign}{adjustment.value:.2f} | "
                f"{adjustment.category.value:<10} | "
                f"{adjustment.description}"
            )

        lines.append("")

        lines.append(
            f"Net Adjustment: {self.total_adjustment:+.2f}"
        )

        return "\n".join(lines)
