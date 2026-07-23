"""Shared framework for committee member decision making."""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.committee_opinion import CommitteeVote


@dataclass(frozen=True)
class DecisionThresholds:
    """
    Confidence thresholds used to convert analysis
    into committee votes.
    """

    strongly_approve: float = 0.90
    approve: float = 0.75
    neutral: float = 0.55
    object: float = 0.35


class DecisionFramework:
    """
    Converts recommendation confidence and discipline-specific
    adjustments into standardized committee votes.
    """

    def __init__(
        self,
        thresholds: DecisionThresholds | None = None,
    ) -> None:

        self._thresholds = (
            thresholds
            or DecisionThresholds()
        )

    def vote(
        self,
        confidence: float,
    ) -> CommitteeVote:

        if confidence >= self._thresholds.strongly_approve:
            return CommitteeVote.STRONGLY_APPROVE

        if confidence >= self._thresholds.approve:
            return CommitteeVote.APPROVE

        if confidence >= self._thresholds.neutral:
            return CommitteeVote.NEUTRAL

        if confidence >= self._thresholds.object:
            return CommitteeVote.OBJECT

        return CommitteeVote.STRONGLY_OBJECT

    @staticmethod
    def clamp(
        confidence: float,
    ) -> float:

        return max(
            0.0,
            min(
                1.0,
                round(confidence, 4),
            ),
        )
