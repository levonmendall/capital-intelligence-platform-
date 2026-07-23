"""CIO reflection and accountability models."""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.metadata import DocumentMetadata


@dataclass
class CIOReflection:
    """Evaluation of prior CIO guidance."""

    previous_guidance_id: str
    reflection_summary: str

    what_we_got_right: list[str] = field(default_factory=list)
    what_we_got_wrong: list[str] = field(default_factory=list)
    assumptions_that_failed: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    changes_to_current_guidance: list[str] = field(default_factory=list)

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def __post_init__(self) -> None:
        if not self.previous_guidance_id.strip():
            raise ValueError("previous_guidance_id cannot be empty")
