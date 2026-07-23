"""Generator for canonical Investment Committee reports."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from intelligence.committee_opinion import CommitteeOpinion
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.investment_committee_report import (
    CommitteeReportEntry,
    InvestmentCommitteeReport,
)


class InvestmentCommitteeReportGenerator:
    """Create report artifacts from final committee decisions."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        identifier_factory: Callable[[], str] | None = None,
    ) -> None:
        self._clock = clock or (
            lambda: datetime.now(timezone.utc)
        )
        self._identifier_factory = (
            identifier_factory
            or (
                lambda: f"icr-{uuid4().hex}"
            )
        )

    def generate(
        self,
        decision: InvestmentCommitteeDecision,
    ) -> InvestmentCommitteeReport:
        """Generate a canonical report from one final decision."""

        if not isinstance(
            decision,
            InvestmentCommitteeDecision,
        ):
            raise TypeError(
                "decision must be an InvestmentCommitteeDecision"
            )

        generated_at = self._clock()

        if not isinstance(generated_at, datetime):
            raise TypeError(
                "clock must return a datetime"
            )

        if generated_at.tzinfo is None:
            raise ValueError(
                "clock must return a timezone-aware datetime"
            )

        report_identifier = self._identifier_factory()

        if not isinstance(report_identifier, str):
            raise TypeError(
                "identifier_factory must return a string"
            )

        vetoes = set(decision.vetoes)

        entries = tuple(
            self._build_entry(
                opinion,
                veto_exercised=opinion in vetoes,
            )
            for opinion in decision.opinions
        )

        return InvestmentCommitteeReport(
            report_identifier=report_identifier,
            generated_at=generated_at,
            decision=decision,
            executive_summary=(
                self._build_executive_summary(
                    decision
                )
            ),
            committee_entries=entries,
            strengths=decision.strengths,
            concerns=decision.concerns,
            required_changes=decision.required_changes,
        )

    @staticmethod
    def _build_entry(
        opinion: CommitteeOpinion,
        *,
        veto_exercised: bool,
    ) -> CommitteeReportEntry:
        return CommitteeReportEntry(
            role=opinion.member,
            vote=opinion.vote,
            confidence=opinion.confidence,
            rationale=opinion.rationale,
            strengths=opinion.strengths,
            concerns=opinion.concerns,
            required_changes=(
                opinion.suggested_changes
            ),
            veto_exercised=veto_exercised,
        )

    @staticmethod
    def _build_executive_summary(
        decision: InvestmentCommitteeDecision,
    ) -> str:
        recommendation = decision.recommendation
        opinions = decision.opinions

        supportive_count = len(
            opinions.supportive
        )
        neutral_count = len(
            opinions.neutral
        )
        opposed_count = len(
            opinions.opposed
        )

        consensus_label = (
            decision.consensus.value
            .replace("_", " ")
            .title()
        )

        summary = (
            f'The Investment Committee reviewed '
            f'"{recommendation.title}" '
            f"for {recommendation.target} and reached "
            f"{consensus_label} with "
            f"{decision.confidence:.1%} confidence. "
            f"The vote included "
            f"{supportive_count} supportive, "
            f"{neutral_count} neutral, and "
            f"{opposed_count} opposed opinion(s)."
        )

        if decision.has_veto:
            summary += (
                f" {len(decision.vetoes)} veto-capable "
                f"committee member(s) exercised a veto."
            )

        if decision.required_changes:
            summary += (
                f" The committee identified "
                f"{len(decision.required_changes)} "
                f"required change(s)."
            )

        return summary
