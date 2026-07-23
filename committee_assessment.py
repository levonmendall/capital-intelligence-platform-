"""Intermediate committee assessment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommitteeAssessment:
    """
    Discipline-specific assessment prior to voting.

    Committee members perform analysis first.
    The DecisionFramework later converts the
    assessment into a CommitteeOpinion.
    """

    adjusted_confidence: float

    rationale: str

    strengths: tuple[str, ...]

    concerns: tuple[str, ...]

    suggested_changes: tuple[str, ...]
