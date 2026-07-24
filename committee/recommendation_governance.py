"""Canonical committee entry point for recommendation governance.

The mature recommendation-governance implementation currently lives in
``intelligence`` for historical reasons. New callers should import the names
from this module so implementation ownership can move into ``committee``
without another caller migration.
"""

from intelligence.investment_committee import (
    InvestmentCommittee as RecommendationInvestmentCommittee,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus as RecommendationCommitteeConsensus,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision as RecommendationCommitteeDecision,
)
from intelligence.investment_policy import (
    InvestmentPolicy as RecommendationCommitteePolicy,
)

__all__ = [
    "RecommendationCommitteeConsensus",
    "RecommendationCommitteeDecision",
    "RecommendationCommitteePolicy",
    "RecommendationInvestmentCommittee",
]
