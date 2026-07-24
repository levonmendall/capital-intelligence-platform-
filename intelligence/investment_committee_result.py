"""Complete result produced by the Investment Committee workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from intelligence.committee_statistics import CommitteeStatistics
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.investment_committee_report import (
    InvestmentCommitteeReport,
)


@dataclass(frozen=True, slots=True)
class InvestmentCommitteeResult:
    """Bundle one decision with its report and analytical statistics."""

    decision: InvestmentCommitteeDecision

    report: InvestmentCommitteeReport

    statistics: CommitteeStatistics

    generated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(
            self.decision,
            InvestmentCommitteeDecision,
        ):
            raise TypeError(
                "decision must be an InvestmentCommitteeDecision"
            )

        if not isinstance(
            self.report,
            InvestmentCommitteeReport,
        ):
            raise TypeError(
                "report must be an InvestmentCommitteeReport"
            )

        if self.report.decision != self.decision:
            raise ValueError(
                "report must reference the result decision"
            )

        if not isinstance(
            self.statistics,
            CommitteeStatistics,
        ):
            raise TypeError(
                "statistics must be CommitteeStatistics"
            )

        if not isinstance(self.generated_at, datetime):
            raise TypeError(
                "generated_at must be a datetime"
            )

        if self.generated_at.tzinfo is None:
            raise ValueError(
                "generated_at must be timezone-aware"
            )
