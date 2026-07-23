"""
Shared decision framework for investment committee members.

Committee members perform discipline-specific analysis and produce a
CommitteeAssessment. The DecisionFramework converts that assessment
into a standardized CommitteeOpinion.

Adjustment aggregation belongs to AdjustmentEngine. Voting and opinion
construction belong to DecisionFramework.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import TYPE_CHECKING

from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
    CommitteeVote,
)

if TYPE_CHECKING:
    from intelligence.committee_member import (
        CommitteeMember,
    )


@dataclass(frozen=True, slots=True)
class DecisionThresholds:
    """
    Confidence thresholds used to determine committee votes.
    """

    strongly_approve: float = 0.90
    approve: float = 0.75
    neutral: float = 0.55
    object: float = 0.35

    def __post_init__(self) -> None:
        """Validate threshold values and ordering."""

        names_and_values = (
            (
                "strongly_approve",
                self.strongly_approve,
            ),
            ("approve", self.approve),
            ("neutral", self.neutral),
            ("object", self.object),
        )

        for name, value in names_and_values:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be numeric."
                )

            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if not 0.0 <= numeric_value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0."
                )

            object.__setattr__(
                self,
                name,
                round(numeric_value, 4),
            )

        if not (
            self.strongly_approve
            > self.approve
            > self.neutral
            > self.object
        ):
            raise ValueError(
                "Thresholds must descend from strongly_approve "
                "through object."
            )


class DecisionFramework:
    """
    Standard committee voting and opinion framework.
    """

    def __init__(
        self,
        thresholds: DecisionThresholds | None = None,
    ) -> None:
        self._thresholds = (
            thresholds
            if thresholds is not None
            else DecisionThresholds()
        )

    @property
    def thresholds(self) -> DecisionThresholds:
        """Return active voting thresholds."""

        return self._thresholds

    @staticmethod
    def clamp(
        confidence: float,
    ) -> float:
        """Clamp confidence into the valid range."""

        if not isinstance(confidence, (int, float)):
            raise TypeError(
                "confidence must be numeric."
            )

        numeric_confidence = float(confidence)

        if not isfinite(numeric_confidence):
            raise ValueError(
                "confidence must be finite."
            )

        return round(
            max(
                0.0,
                min(
                    1.0,
                    numeric_confidence,
                ),
            ),
            4,
        )

    def vote(
        self,
        confidence: float,
    ) -> CommitteeVote:
        """Convert confidence into a standardized vote."""

        confidence = self.clamp(confidence)

        if confidence >= self._thresholds.strongly_approve:
            return CommitteeVote.STRONGLY_APPROVE

        if confidence >= self._thresholds.approve:
            return CommitteeVote.APPROVE

        if confidence >= self._thresholds.neutral:
            return CommitteeVote.NEUTRAL

        if confidence >= self._thresholds.object:
            return CommitteeVote.OBJECT

        return CommitteeVote.STRONGLY_OBJECT

    def build_opinion(
        self,
        *,
        recommendation_identifier: str,
        member: CommitteeMember,
        assessment: CommitteeAssessment,
    ) -> CommitteeOpinion:
        """
        Convert a CommitteeAssessment into a CommitteeOpinion.
        """

        if not isinstance(
            recommendation_identifier,
            str,
        ):
            raise TypeError(
                "recommendation_identifier must be a string."
            )

        recommendation_identifier = (
            recommendation_identifier.strip()
        )

        if not recommendation_identifier:
            raise ValueError(
                "recommendation_identifier cannot be empty."
            )

        if not isinstance(
            assessment,
            CommitteeAssessment,
        ):
            raise TypeError(
                "assessment must be a CommitteeAssessment."
            )

        member_role = member.role

        if not isinstance(
            member_role,
            CommitteeRole,
        ):
            raise TypeError(
                "member.role must be a CommitteeRole."
            )

        confidence = self.clamp(
            assessment.adjusted_confidence
        )

        return CommitteeOpinion(
            recommendation_identifier=
                recommendation_identifier,
            member=member_role,
            vote=self.vote(confidence),
            confidence=confidence,
            rationale=assessment.rationale,
            strengths=assessment.strengths,
            concerns=assessment.concerns,
            suggested_changes=
                assessment.suggested_changes,
        )

    def confidence_band(
        self,
        confidence: float,
    ) -> str:
        """Return a human-readable confidence band."""

        confidence = self.clamp(confidence)

        if confidence >= self._thresholds.strongly_approve:
            return "Very High"

        if confidence >= self._thresholds.approve:
            return "High"

        if confidence >= self._thresholds.neutral:
            return "Moderate"

        if confidence >= self._thresholds.object:
            return "Low"

        return "Very Low"

    def summarize(
        self,
        assessment: CommitteeAssessment,
    ) -> str:
        """Produce a concise governance summary."""

        if not isinstance(
            assessment,
            CommitteeAssessment,
        ):
            raise TypeError(
                "assessment must be a CommitteeAssessment."
            )

        confidence = self.clamp(
            assessment.adjusted_confidence
        )

        vote = self.vote(confidence)

        return (
            f"{vote.value} | "
            f"Base {assessment.base_confidence:.2%} | "
            f"Adjustment "
            f"{assessment.confidence_change:+.2%} | "
            f"Final {confidence:.2%} | "
            f"{len(assessment.strengths)} strengths | "
            f"{len(assessment.concerns)} concerns | "
            f"{len(assessment.suggested_changes)} changes"
        )
