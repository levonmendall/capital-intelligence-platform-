"""Compatibility exports for committee opinion domain models.

The canonical implementations live in intelligence.committee_opinion.
The committee package re-exports them so existing imports continue to work.
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
