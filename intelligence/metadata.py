"""Shared metadata for versioned institutional documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class DocumentStatus(str, Enum):
    """Lifecycle status for institutional documents."""

    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentMetadata:
    """Version and audit metadata attached to institutional records."""

    document_id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1
    created_at: datetime = field(default_factory=utc_now)
    created_by: str = "capital-intelligence-platform"
    supersedes: str | None = None
    status: DocumentStatus = DocumentStatus.DRAFT

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("version must be at least 1")

        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")

        if not self.created_by.strip():
            raise ValueError("created_by cannot be empty")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
