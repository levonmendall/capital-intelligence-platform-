"""Integration tests for the governance package boundary."""

from committee.opinion import (
    CommitteeOpinion as CommitteePackageOpinion,
)
from committee.opinion import (
    CommitteeOpinionSet as CommitteePackageOpinionSet,
)
from committee.opinion import (
    CommitteeRole as CommitteePackageRole,
)
from committee.opinion import (
    CommitteeVote as CommitteePackageVote,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeOpinionSet,
    CommitteeRole,
    CommitteeVote,
)


def test_committee_package_reexports_canonical_opinion_model() -> None:
    assert CommitteePackageOpinion is CommitteeOpinion
    assert CommitteePackageOpinionSet is CommitteeOpinionSet
    assert CommitteePackageRole is CommitteeRole
    assert CommitteePackageVote is CommitteeVote
