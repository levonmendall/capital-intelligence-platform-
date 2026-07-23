"""Domain models for economic and investment themes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThemeCategory(str, Enum):
    """High-level categories for economic themes."""

    GROWTH = "growth"
    INFLATION = "inflation"
    MONETARY_POLICY = "monetary_policy"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    LABOR = "labor"
    CONSUMER = "consumer"
    MANUFACTURING = "manufacturing"
    DEFENSIVE = "defensive"
    STRUCTURAL = "structural"


class ThemeDirection(str, Enum):
    """Expected investment direction associated with a theme."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class EconomicTheme:
    """
    One economic theme derived from the current state and forecast.

    A theme describes an economic force that may influence markets.
    It does not prescribe specific portfolio trades.
    """

    identifier: str
    title: str
    category: ThemeCategory
    direction: ThemeDirection
    confidence: float
    description: str
    supporting_evidence: tuple[str, ...]
    risks: tuple[str, ...]
    affected_asset_classes: tuple[str, ...]
    expected_duration_months: int

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier cannot be empty")

        if not self.title.strip():
            raise ValueError("title cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.description.strip():
            raise ValueError("description cannot be empty")

        if not self.supporting_evidence:
            raise ValueError(
                "supporting_evidence must contain at least one item"
            )

        if not all(
            evidence.strip()
            for evidence in self.supporting_evidence
        ):
            raise ValueError(
                "supporting_evidence cannot contain empty values"
            )

        if not all(risk.strip() for risk in self.risks):
            raise ValueError(
                "risks cannot contain empty values"
            )

        if not self.affected_asset_classes:
            raise ValueError(
                "affected_asset_classes must contain at least one item"
            )

        if not all(
            asset_class.strip()
            for asset_class in self.affected_asset_classes
        ):
            raise ValueError(
                "affected_asset_classes cannot contain empty values"
            )

        if self.expected_duration_months < 1:
            raise ValueError(
                "expected_duration_months must be at least 1"
            )


@dataclass(frozen=True)
class ThemeSet:
    """Collection of themes generated from one forecast."""

    themes: tuple[EconomicTheme, ...]
    confidence: float
    summary: str

    def __post_init__(self) -> None:
        if not self.themes:
            raise ValueError(
                "themes must contain at least one EconomicTheme"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

        identifiers = [
            theme.identifier
            for theme in self.themes
        ]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError(
                "theme identifiers must be unique"
            )

    def by_category(
        self,
        category: ThemeCategory,
    ) -> tuple[EconomicTheme, ...]:
        """Return all themes belonging to a category."""

        return tuple(
            theme
            for theme in self.themes
            if theme.category == category
        )

    def highest_confidence(self) -> EconomicTheme:
        """Return the theme with the highest confidence."""

        return max(
            self.themes,
            key=lambda theme: theme.confidence,
        )
