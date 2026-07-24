"""Public intelligence API with lazy compatibility exports.

Lazy loading keeps the public API stable while preventing package
initialization from creating cycles with collective governance in
``committee``.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORTS = {
    "ChangeCondition": (
        "intelligence.cio_guidance",
        "ChangeCondition",
    ),
    "ChiefInvestmentOfficer": (
        "intelligence.cio",
        "ChiefInvestmentOfficer",
    ),
    "CIOBriefing": (
        "intelligence.briefing",
        "CIOBriefing",
    ),
    "CIOGuidance": (
        "intelligence.cio_guidance",
        "CIOGuidance",
    ),
    "CIOReflection": (
        "intelligence.reflection",
        "CIOReflection",
    ),
    "ConfidenceScores": (
        "intelligence.cio_guidance",
        "ConfidenceScores",
    ),
    "DocumentMetadata": (
        "intelligence.metadata",
        "DocumentMetadata",
    ),
    "DocumentStatus": (
        "intelligence.metadata",
        "DocumentStatus",
    ),
    "GuidanceSynthesizer": (
        "intelligence.cio",
        "GuidanceSynthesizer",
    ),
    "ScenarioProbability": (
        "intelligence.cio_guidance",
        "ScenarioProbability",
    ),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    """Load one public export on first access."""

    try:
        module_name, attribute_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from exc

    value = getattr(
        import_module(module_name),
        attribute_name,
    )
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return public lazy exports for interactive discovery."""

    return sorted(set(globals()) | set(__all__))
