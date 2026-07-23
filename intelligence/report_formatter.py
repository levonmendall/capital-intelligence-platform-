"""
Formatting utilities for Investment Committee reports.

This module converts canonical InvestmentCommitteeReport objects into
human-readable formats without modifying the underlying report.

Additional output formats (HTML, PDF, JSON, email, etc.) should build
upon this formatter.
"""

from __future__ import annotations

from intelligence.investment_committee_report import (
    CommitteeReportEntry,
    InvestmentCommitteeReport,
)


class ReportFormatter:
    """Formats Investment Committee reports."""

    INDENT = "    "

    #
    # Public API
    #

    def to_text(
        self,
        report: InvestmentCommitteeReport,
    ) -> str:
        """Return a plain-text report."""

        self._validate(report)

        lines: list[str] = []

        lines.extend(self._header(report))
        lines.append("")

        lines.extend(self._executive_summary(report))
        lines.append("")

        lines.extend(self._decision(report))
        lines.append("")

        lines.extend(self._committee_breakdown(report))
        lines.append("")

        lines.extend(
            self._bullet_section(
                "Strengths",
                report.strengths,
            )
        )

        lines.append("")

        lines.extend(
            self._bullet_section(
                "Concerns",
                report.concerns,
            )
        )

        lines.append("")

        lines.extend(
            self._bullet_section(
                "Required Changes",
                report.required_changes,
            )
        )

        return "\n".join(lines)

    def to_markdown(
        self,
        report: InvestmentCommitteeReport,
    ) -> str:
        """Return Markdown output."""

        self._validate(report)

        lines: list[str] = []

        lines.append("# Investment Committee Report")
        lines.append("")

        lines.append(
            f"**Recommendation:** "
            f"{report.recommendation_title}"
        )

        lines.append(
            f"**Consensus:** "
            f"{report.consensus.name.replace('_', ' ').title()}"
        )

        lines.append(
            f"**Confidence:** "
            f"{report.confidence:.1%}"
        )

        lines.append("")

        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.executive_summary)
        lines.append("")

        lines.append("## Committee Opinions")
        lines.append("")

        for entry in report.committee_entries:

            lines.append(
                f"### {entry.role.name.title()}"
            )

            lines.append(
                f"- Vote: {entry.vote.name.title()}"
            )

            lines.append(
                f"- Confidence: {entry.confidence:.1%}"
            )

            if entry.veto_exercised:
                lines.append("- **VETO**")

            lines.append("")
            lines.append(entry.rationale)
            lines.append("")

        self._append_markdown_list(
            lines,
            "Strengths",
            report.strengths,
        )

        self._append_markdown_list(
            lines,
            "Concerns",
            report.concerns,
        )

        self._append_markdown_list(
            lines,
            "Required Changes",
            report.required_changes,
        )

        return "\n".join(lines)

    #
    # Internal helpers
    #

    @staticmethod
    def _validate(
        report: InvestmentCommitteeReport,
    ) -> None:

        if not isinstance(
            report,
            InvestmentCommitteeReport,
        ):
            raise TypeError(
                "report must be an InvestmentCommitteeReport"
            )

    def _header(
        self,
        report: InvestmentCommitteeReport,
    ) -> list[str]:

        return [
            "=" * 70,
            "INVESTMENT COMMITTEE REPORT",
            "=" * 70,
            f"Report ID : {report.report_identifier}",
            f"Generated : {report.generated_at.isoformat()}",
        ]

    def _executive_summary(
        self,
        report: InvestmentCommitteeReport,
    ) -> list[str]:

        return [
            "EXECUTIVE SUMMARY",
            "-" * 70,
            report.executive_summary,
        ]

    def _decision(
        self,
        report: InvestmentCommitteeReport,
    ) -> list[str]:

        return [
            "DECISION",
            "-" * 70,
            f"Recommendation : {report.recommendation_title}",
            f"Consensus      : "
            f"{report.consensus.name.replace('_',' ').title()}",
            f"Confidence     : {report.confidence:.1%}",
            f"Approved       : {'Yes' if report.approved else 'No'}",
            f"Committee Size : {report.committee_count}",
            f"Supportive     : {report.supportive_count}",
            f"Neutral        : {report.neutral_count}",
            f"Opposed        : {report.opposed_count}",
            f"Veto           : {'Yes' if report.has_veto else 'No'}",
        ]

    def _committee_breakdown(
        self,
        report: InvestmentCommitteeReport,
    ) -> list[str]:

        lines = [
            "COMMITTEE BREAKDOWN",
            "-" * 70,
        ]

        for entry in report.committee_entries:

            lines.extend(
                self._committee_entry(entry)
            )

            lines.append("")

        return lines

    def _committee_entry(
        self,
        entry: CommitteeReportEntry,
    ) -> list[str]:

        lines = [
            entry.role.name.replace(
                "_",
                " ",
            ).title(),
            self.INDENT
            + f"Vote       : {entry.vote.name.title()}",
            self.INDENT
            + f"Confidence : {entry.confidence:.1%}",
            self.INDENT
            + f"Rationale  : {entry.rationale}",
        ]

        if entry.veto_exercised:
            lines.append(
                self.INDENT
                + "VETO EXERCISED"
            )

        return lines

    @staticmethod
    def _bullet_section(
        title: str,
        items: tuple[str, ...],
    ) -> list[str]:

        lines = [
            title.upper(),
            "-" * 70,
        ]

        if not items:

            lines.append("None")

            return lines

        for item in items:

            lines.append(f"• {item}")

        return lines

    @staticmethod
    def _append_markdown_list(
        lines: list[str],
        title: str,
        values: tuple[str, ...],
    ) -> None:

        lines.append(f"## {title}")
        lines.append("")

        if not values:

            lines.append("_None_")
            lines.append("")
            return

        for value in values:

            lines.append(f"- {value}")

        lines.append("")
