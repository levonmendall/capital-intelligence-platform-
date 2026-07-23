"""Institutional decision journal models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from committee.meeting import CommitteeMeeting
from intelligence.cio_guidance import CIOGuidance
from intelligence.metadata import DocumentMetadata
from intelligence.reflection import CIOReflection
from portfolio_managers.response import PortfolioManagerResponse


@dataclass
class DecisionJournalEntry:
    """Complete record of one institutional decision cycle."""

    committee_meeting: CommitteeMeeting
    cio_guidance: CIOGuidance

    portfolio_responses: list[PortfolioManagerResponse] = field(
        default_factory=list
    )
    executed_trades: list[Any] = field(default_factory=list)
    portfolio_results: dict[str, Any] = field(default_factory=dict)
    reflection: CIOReflection | None = None

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def response_for_mandate(
        self,
        mandate_id: str,
    ) -> PortfolioManagerResponse | None:
        """Return the response associated with a mandate."""

        for response in self.portfolio_responses:
            if response.mandate_id.value == mandate_id:
                return response

        return None
