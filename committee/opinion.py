"""Investment committee opinion model."""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.metadata import DocumentMetadata


@dataclass
class CommitteeOpinion:
    """Structured view issued by one investment committee member."""

    member: str
    specialty: str
    outlook: str
    confidence: float
    recommendation: str

    evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def __post_init__(self) -> None:
        if not self.member.strip():
            raise ValueError("member cannot be empty")

        if not self.specialty.strip():
            raise ValueError("specialty cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
