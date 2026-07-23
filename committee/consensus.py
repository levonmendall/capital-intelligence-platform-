"""Investment committee consensus model."""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.metadata import DocumentMetadata


@dataclass
class CommitteeConsensus:
    """Consensus produced after reviewing committee opinions."""

    majority_view: str
    confidence: float

    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    minority_opinions: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def __post_init__(self) -> None:
        if not self.majority_view.strip():
            raise ValueError("majority_view cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
