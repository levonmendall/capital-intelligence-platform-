"""
Intermediate committee assessment domain model.

A committee member analyzes an investment recommendation and produces
a CommitteeAssessment. The assessment preserves:

- base confidence
- proposed and applied score adjustments
- adjusted confidence
- analytical rationale
- strengths
- concerns
- suggested changes

The DecisionFramework later converts the assessment into a standardized
CommitteeOpinion.
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.committee_adjustment import (
    AdjustmentSet,
)


@dataclass(frozen=True, slots=True)
class CommitteeAssessment:
    """
    Result of a committee member's independent analysis.
    """

    base_confidence: float
    adjusted_confidence: float
    adjustments: AdjustmentSet
    rationale: str
    strengths: tuple[str, ...]
    concerns: tuple[str, ...]
    suggested_changes: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate assessment values."""

        for name, value in (
            ("base_confidence", self.base_confidence),
            (
                "adjusted_confidence",
                self.adjusted_confidence,
            ),
        ):
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be numeric."
                )

            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0."
                )

            object.__setattr__(
                self,
                name,
                round(float(value), 4),
            )

        if not isinstance(
            self.adjustments,
            AdjustmentSet,
        ):
            raise TypeError(
                "adjustments must be an AdjustmentSet."
            )

        expected_confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    (
                        self.base_confidence
                        + self.adjustments
                        .total_applied_adjustment
                    ),
                ),
            ),
            4,
        )

        if (
            abs(
                self.adjusted_confidence
                - expected_confidence
            )
            > 0.0001
        ):
            raise ValueError(
                "adjusted_confidence must equal base_confidence "
                "plus the applied adjustment total after clamping."
            )

        if not isinstance(self.rationale, str):
            raise TypeError(
                "rationale must be a string."
            )

        rationale = self.rationale.strip()

        if not rationale:
            raise ValueError(
                "rationale cannot be empty."
            )

        object.__setattr__(
            self,
            "rationale",
            rationale,
        )

        self._validate_collection(
            self.strengths,
            "strengths",
        )

        self._validate_collection(
            self.concerns,
            "concerns",
        )

        self._validate_collection(
            self.suggested_changes,
            "suggested_changes",
        )

    @staticmethod
    def _validate_collection(
        values: tuple[str, ...],
        name: str,
    ) -> None:
        """Validate a tuple of descriptive strings."""

        if not isinstance(values, tuple):
            raise TypeError(
                f"{name} must be a tuple."
            )

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"Every item in {name} must be a string."
                )

            if not value.strip():
                raise ValueError(
                    f"{name} cannot contain blank strings."
                )

    @property
    def confidence_change(self) -> float:
        """Net change from base to adjusted confidence."""

        return round(
            self.adjusted_confidence
            - self.base_confidence,
            4,
        )

    @property
    def is_high_confidence(self) -> bool:
        """Whether the assessment is high conviction."""

        return self.adjusted_confidence >= 0.80

    @property
    def has_concerns(self) -> bool:
        """Whether concerns were identified."""

        return bool(self.concerns)

    @property
    def requires_revision(self) -> bool:
        """Whether revisions were recommended."""

        return bool(self.suggested_changes)

    @property
    def was_policy_constrained(self) -> bool:
        """Whether policy changed any proposed adjustment."""

        return bool(self.adjustments.constrained)

    def summary(self) -> str:
        """Produce a concise assessment summary."""

        return (
            f"Base Confidence: {self.base_confidence:.2%} | "
            f"Adjustment: {self.confidence_change:+.2%} | "
            f"Final Confidence: "
            f"{self.adjusted_confidence:.2%} | "
            f"Strengths: {len(self.strengths)} | "
            f"Concerns: {len(self.concerns)} | "
            f"Suggested Changes: "
            f"{len(self.suggested_changes)}"
        )
