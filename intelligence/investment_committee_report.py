"""Canonical reporting models for Investment Committee decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from intelligence.committee_opinion import (
    CommitteeRole,
    CommitteeVote,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)


def _validate_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")

    return normalized


def _validate_text_tuple(
    values: tuple[str, ...],
    *,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")

    return tuple(
        _validate_text(
            value,
            field_name=f"{field_name}[{index}]",
        )
        for index, value in enumerate(values)
    )


@dataclass(frozen=True, slots=True)
class CommitteeReportEntry:
    """Report-ready summary of one specialist committee opinion."""

    role: CommitteeRole
    vote: CommitteeVote
    confidence: float
    rationale: str
    strengths: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    required_changes: tuple[str, ...] = ()
    veto_exercised: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.role, CommitteeRole):
            raise TypeError("role must be a CommitteeRole")

        if not isinstance(self.vote, CommitteeVote):
            raise TypeError("vote must be a CommitteeVote")

        if isinstance(self.confidence, bool) or not isinstance(
            self.confidence,
            (int, float),
        ):
            raise TypeError("confidence must be numeric")

        confidence = float(self.confidence)

        if not isfinite(confidence):
            raise ValueError("confidence must be finite")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        rationale = _validate_text(
            self.rationale,
            field_name="rationale",
        )
        strengths = _validate_text_tuple(
            self.strengths,
            field_name="strengths",
        )
        concerns = _validate_text_tuple(
            self.concerns,
            field_name="concerns",
        )
        required_changes = _validate_text_tuple(
            self.required_changes,
            field_name="required_changes",
        )

        if not isinstance(self.veto_exercised, bool):
            raise TypeError("veto_exercised must be a bool")

        if self.veto_exercised and not self.vote.is_opposed:
            raise ValueError(
                "a veto can only be exercised with an opposed vote"
            )

        object.__setattr__(
            self,
            "confidence",
            round(confidence, 4),
        )
        object.__setattr__(
            self,
            "rationale",
            rationale,
        )
        object.__setattr__(
            self,
            "strengths",
            strengths,
        )
        object.__setattr__(
            self,
            "concerns",
            concerns,
        )
        object.__setattr__(
            self,
            "required_changes",
            required_changes,
        )

    @property
    def supportive(self) -> bool:
        return self.vote.is_supportive

    @property
    def opposed(self) -> bool:
        return self.vote.is_opposed

    @property
    def neutral(self) -> bool:
        return self.vote is CommitteeVote.NEUTRAL


@dataclass(frozen=True, slots=True)
class InvestmentCommitteeReport:
    """Immutable canonical report for one committee decision."""

    report_identifier: str
    generated_at: datetime
    decision: InvestmentCommitteeDecision
    executive_summary: str
    committee_entries: tuple[CommitteeReportEntry, ...]
    strengths: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    required_changes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        report_identifier = _validate_text(
            self.report_identifier,
            field_name="report_identifier",
        )

        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime")

        if self.generated_at.tzinfo is None:
            raise ValueError(
                "generated_at must be timezone-aware"
            )

        if not isinstance(
            self.decision,
            InvestmentCommitteeDecision,
        ):
            raise TypeError(
                "decision must be an InvestmentCommitteeDecision"
            )

        executive_summary = _validate_text(
            self.executive_summary,
            field_name="executive_summary",
        )

        if not isinstance(self.committee_entries, tuple):
            raise TypeError(
                "committee_entries must be a tuple"
            )

        if not self.committee_entries:
            raise ValueError(
                "committee_entries cannot be empty"
            )

        if not all(
            isinstance(entry, CommitteeReportEntry)
            for entry in self.committee_entries
        ):
            raise TypeError(
                "committee_entries must contain "
                "CommitteeReportEntry objects"
            )

        roles = [
            entry.role
            for entry in self.committee_entries
        ]

        if len(roles) != len(set(roles)):
            raise ValueError(
                "committee_entries cannot contain duplicate roles"
            )

        decision_roles = {
            opinion.member
            for opinion in self.decision.opinions
        }

        if set(roles) != decision_roles:
            raise ValueError(
                "committee_entries must represent "
                "every decision opinion"
            )

        strengths = _validate_text_tuple(
            self.strengths,
            field_name="strengths",
        )
        concerns = _validate_text_tuple(
            self.concerns,
            field_name="concerns",
        )
        required_changes = _validate_text_tuple(
            self.required_changes,
            field_name="required_changes",
        )

        object.__setattr__(
            self,
            "report_identifier",
            report_identifier,
        )
        object.__setattr__(
            self,
            "executive_summary",
            executive_summary,
        )
        object.__setattr__(
            self,
            "strengths",
            strengths,
        )
        object.__setattr__(
            self,
            "concerns",
            concerns,
        )
        object.__setattr__(
            self,
            "required_changes",
            required_changes,
        )

    @property
    def recommendation_identifier(self) -> str:
        return self.decision.recommendation.identifier

    @property
    def recommendation_title(self) -> str:
        return self.decision.recommendation.title

    @property
    def consensus(self) -> InvestmentCommitteeConsensus:
        return self.decision.consensus

    @property
    def confidence(self) -> float:
        return self.decision.confidence

    @property
    def approved(self) -> bool:
        return self.decision.approved

    @property
    def has_veto(self) -> bool:
        return self.decision.has_veto

    @property
    def committee_count(self) -> int:
        return len(self.committee_entries)

    @property
    def supportive_count(self) -> int:
        return sum(
            entry.supportive
            for entry in self.committee_entries
        )

    @property
    def neutral_count(self) -> int:
        return sum(
            entry.neutral
            for entry in self.committee_entries
        )

    @property
    def opposed_count(self) -> int:
        return sum(
            entry.opposed
            for entry in self.committee_entries
        )
