"""Daily CIO briefing models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from intelligence.metadata import DocumentMetadata


@dataclass
class CIOBriefing:
    """Standardized information packet presented to the committee."""

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    macro: dict[str, Any] = field(default_factory=dict)
    markets: dict[str, Any] = field(default_factory=dict)
    credit: dict[str, Any] = field(default_factory=dict)
    valuation: dict[str, Any] = field(default_factory=dict)
    sentiment: dict[str, Any] = field(default_factory=dict)
    commodities: dict[str, Any] = field(default_factory=dict)
    global_markets: dict[str, Any] = field(default_factory=dict)

    major_risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    upcoming_catalysts: list[str] = field(default_factory=list)

    executive_summary: str = ""

    def is_empty(self) -> bool:
        """Return True when the briefing contains no analytical data."""

        sections = (
            self.macro,
            self.markets,
            self.credit,
            self.valuation,
            self.sentiment,
            self.commodities,
            self.global_markets,
        )

        return not any(sections)
