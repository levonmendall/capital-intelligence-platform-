"""Compatibility exports for committee opinion domain models.

Canonical implementations live in intelligence.committee_opinion.
This module preserves the older committee.opinion import path.
"""

from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeOpinionSet,
    CommitteeRole,
    CommitteeVote,
)

__all__ = [
    "CommitteeOpinion",
    "CommitteeOpinionSet",
    "CommitteeRole",
    "CommitteeVote",
]
