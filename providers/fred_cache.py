"""Deterministic cache contracts for FRED payloads."""

from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable


def _aware_datetime(value: object, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def fred_cache_key(
    endpoint: str,
    parameters: Mapping[str, Any],
) -> str:
    """Return a stable request key without persisting credentials."""

    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("endpoint must be a non-empty string")
    sanitized = {
        str(key): value
        for key, value in parameters.items()
        if str(key).lower() != "api_key"
    }
    canonical = json.dumps(
        {
            "endpoint": endpoint.strip(),
            "parameters": sanitized,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class FREDCacheRecord:
    """One immutable snapshot of a successful provider response."""

    key: str
    payload: dict[str, Any]
    retrieved_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("key must be a non-empty string")
        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dictionary")
        _aware_datetime(
            self.retrieved_at,
            field_name="retrieved_at",
        )
        try:
            normalized = json.loads(json.dumps(self.payload))
        except (TypeError, ValueError) as error:
            raise ValueError(
                "payload must contain JSON-serializable values"
            ) from error
        object.__setattr__(self, "key", self.key.strip())
        object.__setattr__(self, "payload", normalized)

    def copy(self) -> FREDCacheRecord:
        """Return a defensive copy of this cache record."""

        return FREDCacheRecord(
            key=self.key,
            payload=deepcopy(self.payload),
            retrieved_at=self.retrieved_at,
        )


@runtime_checkable
class FREDCache(Protocol):
    """Storage boundary used by the FRED provider."""

    def get(self, key: str) -> FREDCacheRecord | None:
        """Return a cached response if present."""

    def put(self, record: FREDCacheRecord) -> None:
        """Persist a successful response."""


class MemoryFREDCache:
    """Process-local cache suitable for tests and short-lived workers."""

    def __init__(self) -> None:
        self._records: dict[str, FREDCacheRecord] = {}

    def get(self, key: str) -> FREDCacheRecord | None:
        record = self._records.get(key)
        return record.copy() if record is not None else None

    def put(self, record: FREDCacheRecord) -> None:
        if not isinstance(record, FREDCacheRecord):
            raise TypeError("record must be a FREDCacheRecord")
        self._records[record.key] = record.copy()


class JsonFREDCache:
    """Atomic JSON cache for local development and offline operation."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if self.path.exists() and self.path.is_dir():
            raise ValueError("cache path must be a file")

    def get(self, key: str) -> FREDCacheRecord | None:
        records = self._read_records()
        value = records.get(key)
        if value is None:
            return None
        try:
            return FREDCacheRecord(
                key=key,
                payload=value["payload"],
                retrieved_at=datetime.fromisoformat(
                    value["retrieved_at"]
                ),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid FRED cache record for key {key}."
            ) from error

    def put(self, record: FREDCacheRecord) -> None:
        if not isinstance(record, FREDCacheRecord):
            raise TypeError("record must be a FREDCacheRecord")
        records = self._read_records()
        records[record.key] = {
            "payload": record.payload,
            "retrieved_at": record.retrieved_at.isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(
            f".{self.path.name}.{os.getpid()}.tmp"
        )
        temporary.write_text(
            json.dumps(records, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        os.replace(temporary, self.path)

    def _read_records(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(
                self.path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(
                f"Unable to read FRED cache at {self.path}."
            ) from error
        if not isinstance(payload, dict):
            raise ValueError("FRED cache root must be an object")
        return payload
