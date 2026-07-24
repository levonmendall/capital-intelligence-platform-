"""End-to-end institutional workflow for one investment recommendation."""

from __future__ import annotations

from intelligence.committee_statistics import (
    CommitteeStatisticsCalculator,
)
from intelligence.investment_committee_report_generator import (
    InvestmentCommitteeReportGenerator,
)
from intelligence.investment_committee_result import (
    InvestmentCommitteeResult,
)
from intelligence.recommendation import InvestmentRecommendation

from committee.recommendation_governance import (
    RecommendationInvestmentCommittee,
)


class InstitutionalDecisionWorkflow:
    """Turn one immutable recommendation into auditable decision artifacts."""

    def __init__(
        self,
        *,
        committee: RecommendationInvestmentCommittee | None = None,
        report_generator: InvestmentCommitteeReportGenerator | None = None,
        statistics_calculator: CommitteeStatisticsCalculator | None = None,
    ) -> None:
        resolved_committee = (
            committee or RecommendationInvestmentCommittee()
        )
        resolved_report_generator = (
            report_generator or InvestmentCommitteeReportGenerator()
        )
        resolved_statistics_calculator = (
            statistics_calculator or CommitteeStatisticsCalculator()
        )

        if not isinstance(
            resolved_committee,
            RecommendationInvestmentCommittee,
        ):
            raise TypeError(
                "committee must be a RecommendationInvestmentCommittee"
            )
        if not isinstance(
            resolved_report_generator,
            InvestmentCommitteeReportGenerator,
        ):
            raise TypeError(
                "report_generator must be an "
                "InvestmentCommitteeReportGenerator"
            )
        if not isinstance(
            resolved_statistics_calculator,
            CommitteeStatisticsCalculator,
        ):
            raise TypeError(
                "statistics_calculator must be a "
                "CommitteeStatisticsCalculator"
            )

        self._committee = resolved_committee
        self._report_generator = resolved_report_generator
        self._statistics_calculator = resolved_statistics_calculator

    @property
    def committee(self) -> RecommendationInvestmentCommittee:
        """Return the committee used by this workflow."""

        return self._committee

    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> InvestmentCommitteeResult:
        """Evaluate a recommendation and return one consistent result bundle."""

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an InvestmentRecommendation"
            )

        decision = self._committee.evaluate(recommendation)
        report = self._report_generator.generate(decision)
        statistics = self._statistics_calculator.calculate(decision)

        return InvestmentCommitteeResult(
            decision=decision,
            report=report,
            statistics=statistics,
            generated_at=report.generated_at,
        )


__all__ = ["InstitutionalDecisionWorkflow"]
