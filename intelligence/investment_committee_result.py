@dataclass(frozen=True, slots=True)
class InvestmentCommitteeResult:

    decision: InvestmentCommitteeDecision

    report: InvestmentCommitteeReport

    statistics: CommitteeStatistics

    generated_at: datetime
