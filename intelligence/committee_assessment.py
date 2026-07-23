"""
Intermediate committee assessment domain models.

Committee members should first analyze an investment recommendation and
produce a CommitteeAssessment. The DecisionFramework is then responsible
for converting that assessment into a standardized CommitteeOpinion.

This separation keeps analysis independent from governance and allows
all committee members to share identical voting behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommitteeAssessment:
    """
    Result of a committee member's independent analysis.

    A CommitteeAssessment intentionally contains no vote. It represents
    only the analytical conclusion reached by a committee member.

    The DecisionFramework converts this assessment into a
    CommitteeOpinion using standardized voting thresholds.
    """

    adjusted_confidence: float

    rationale: str

    strengths: tuple[str, ...]

    concerns: tuple[str, ...]

    suggested_changes: tuple[str, ...]

    def __post_init__(self) -> None:
        """
        Validate assessment values.
        """

        if not 0.0 <= self.adjusted_confidence <= 1.0:
            raise ValueError(
                "adjusted_confidence must be between 0.0 and 1.0."
            )

        if not self.rationale.strip():
            raise ValueError(
                "rationale cannot be empty."
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
        """
        Validate a tuple of descriptive strings.
        """

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
    def is_high_confidence(self) -> bool:
        """
        Returns True for assessments considered high conviction.
        """

        return self.adjusted_confidence >= 0.80

    @property
    def has_concerns(self) -> bool:
        """
        Returns True if concerns were identified.
        """

        return bool(self.concerns)

    @property
    def requires_revision(self) -> bool:
        """
        Returns True if changes are recommended before approval.
        """

        return bool(self.suggested_changes)

    def summary(self) -> str:
        """
        Produce a concise human-readable summary.
        """

        return (
            f"Confidence: {self.adjusted_confidence:.2%} | "
            f"Strengths: {len(self.strengths)} | "
            f"Concerns: {len(self.concerns)} | "
            f"Suggested Changes: {len(self.suggested_changes)}"
        )
