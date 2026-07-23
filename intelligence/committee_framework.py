"""
Shared decision framework for investment committee members.

Committee members perform analysis by producing a CommitteeAssessment.
The DecisionFramework is responsible for converting that assessment into
a standardized CommitteeOpinion.

This separation ensures every committee member follows identical voting,
confidence normalization, and opinion construction rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeVote,
)


@dataclass(frozen=True, slots=True)
class DecisionThresholds:
    """
    Confidence thresholds used to determine committee votes.

    Thresholds are evaluated from highest to lowest confidence.
    """

    strongly_approve: float = 0.90

    approve: float = 0.75

    neutral: float = 0.55

    object: float = 0.35

    def __post_init__(self) -> None:
        """
        Ensure thresholds are valid and ordered correctly.
        """

        values = (
            self.strongly_approve,
            self.approve,
            self.neutral,
            self.object,
        )

        for value in values:

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    "Decision thresholds must be between 0.0 and 1.0."
                )

        if not (
            self.strongly_approve
            > self.approve
            > self.neutral
            > self.object
        ):
            raise ValueError(
                "Thresholds must descend from strongest approval "
                "to strongest objection."
            )


class DecisionFramework:
    """
    Standard committee voting framework.

    Responsibilities
    ----------------
    • Normalize confidence
    • Convert confidence to votes
    • Construct CommitteeOpinion objects
    • Keep every committee member consistent
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
        """
        Return active voting thresholds.
        """

        return self._thresholds

    @staticmethod
    def clamp(
        confidence: float,
    ) -> float:
        """
        Clamp confidence into the valid range.

        Confidence is rounded to four decimal places to provide
        deterministic output throughout the platform.
        """

        return round(
            max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            ),
            4,
        )

    def vote(
        self,
        confidence: float,
    ) -> CommitteeVote:
        """
        Convert normalized confidence into a committee vote.
        """

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
        member,
        assessment: CommitteeAssessment,
    ) -> CommitteeOpinion:
        """
        Convert a CommitteeAssessment into a CommitteeOpinion.

        Parameters
        ----------
        recommendation_identifier
            Identifier of the recommendation being evaluated.

        member
            CommitteeMember performing the evaluation.

        assessment
            Result of the committee member's analysis.
        """

        confidence = self.clamp(
            assessment.adjusted_confidence
        )

        return CommitteeOpinion(
            recommendation_identifier=
                recommendation_identifier,

            member=member.role,

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
        """
        Return a human-readable confidence classification.
        """

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
        """
        Produce a concise summary suitable for logging
        and audit records.
        """

        confidence = self.clamp(
            assessment.adjusted_confidence
        )

        vote = self.vote(confidence)

        return (
            f"{vote.value} | "
            f"{confidence:.2%} | "
            f"{len(assessment.strengths)} strengths | "
            f"{len(assessment.concerns)} concerns | "
            f"{len(assessment.suggested_changes)} changes"
        )
