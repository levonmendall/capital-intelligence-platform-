"""Investment Committee consensus states."""

from __future__ import annotations

from enum import Enum


class InvestmentCommitteeConsensus(str, Enum):
    """
    Final consensus reached by the Investment Committee.
    """

    STRONG_APPROVAL = "strong_approval"
    APPROVAL = "approval"
    APPROVAL_WITH_CONDITIONS = (
        "approval_with_conditions"
    )
    DEFER = "defer"
    REJECT = "reject"

    @property
    def approved(self) -> bool:
        return self in {
            self.STRONG_APPROVAL,
            self.APPROVAL,
            self.APPROVAL_WITH_CONDITIONS,
        }

    @property
    def requires_changes(self) -> bool:
        return self is self.APPROVAL_WITH_CONDITIONS

    @property
    def terminal(self) -> bool:
        return self in {
            self.STRONG_APPROVAL,
            self.APPROVAL,
            self.REJECT,
        }
