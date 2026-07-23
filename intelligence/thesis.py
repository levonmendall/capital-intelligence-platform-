"""Domain models for explainable investment theses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from intelligence.theme import ThemeCategory


class ThesisDirection(str, Enum):
    """Directional investment implication of a thesis."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    SELECTIVE = "selective"
    NEUTRAL = "neutral"


class ThesisHorizon(str, Enum):
    """Expected time horizon for an investment thesis."""

    TACTICAL = "tactical"
    CYCLICAL = "cyclical"
    STRUCTURAL = "structural"


class ThesisStatus(str, Enum):
    """Current status of an investment thesis."""

    ACTIVE = "active"
    WATCH = "watch"
    INVALIDATED = "invalidated"


@dataclass(frozen=True)
class InvestmentThesis:
    """
    One explainable investment proposition derived from an economic theme.

    The thesis identifies likely beneficiaries and losers, but it does not
    prescribe trades, position sizes, or portfolio weights.
    """

    identifier: str
    title: str
    source_theme_identifier: str
    source_theme_category: ThemeCategory
    direction: ThesisDirection
    horizon: ThesisHorizon
    status: ThesisStatus
    confidence: float
    proposition: str
    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    beneficiaries: tuple[str, ...]
    losers: tuple[str, ...]
    catalysts: tuple[str, ...]
    risks: tuple[str, ...]
    increase_conviction_conditions: tuple[str, ...]
    reduce_conviction_conditions: tuple[str, ...]
    invalidation_conditions: tuple[str, ...]
    expected_duration_months: int

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier cannot be empty")

        if not self.title.strip():
            raise ValueError("title cannot be empty")

        if not self.source_theme_identifier.strip():
            raise ValueError(
                "source_theme_identifier cannot be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.proposition.strip():
            raise ValueError("proposition cannot be empty")

        self._validate_non_empty_tuple(
            self.supporting_evidence,
            "supporting_evidence",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.contradicting_evidence,
            "contradicting_evidence",
            require_items=False,
        )

        self._validate_non_empty_tuple(
            self.beneficiaries,
            "beneficiaries",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.losers,
            "losers",
            require_items=False,
        )

        self._validate_non_empty_tuple(
            self.catalysts,
            "catalysts",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.risks,
            "risks",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.increase_conviction_conditions,
            "increase_conviction_conditions",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.reduce_conviction_conditions,
            "reduce_conviction_conditions",
            require_items=True,
        )

        self._validate_non_empty_tuple(
            self.invalidation_conditions,
            "invalidation_conditions",
            require_items=True,
        )

        if self.expected_duration_months < 1:
            raise ValueError(
                "expected_duration_months must be at least 1"
            )

    @staticmethod
    def _validate_non_empty_tuple(
        values: tuple[str, ...],
        field_name: str,
        *,
        require_items: bool,
    ) -> None:
        if require_items and not values:
            raise ValueError(
                f"{field_name} must contain at least one item"
            )

        if not all(value.strip() for value in values):
            raise ValueError(
                f"{field_name} cannot contain empty values"
            )


@dataclass(frozen=True)
class InvestmentThesisSet:
    """Collection of investment theses generated from one ThemeSet."""

    theses: tuple[InvestmentThesis, ...]
    confidence: float
    summary: str

    def __post_init__(self) -> None:
        if not self.theses:
            raise ValueError(
                "theses must contain at least one InvestmentThesis"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

        identifiers = [
            thesis.identifier
            for thesis in self.theses
        ]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError(
                "thesis identifiers must be unique"
            )

    def active(self) -> tuple[InvestmentThesis, ...]:
        """Return all active investment theses."""

        return tuple(
            thesis
            for thesis in self.theses
            if thesis.status == ThesisStatus.ACTIVE
        )

    def by_direction(
        self,
        direction: ThesisDirection,
    ) -> tuple[InvestmentThesis, ...]:
        """Return all theses with the requested direction."""

        return tuple(
            thesis
            for thesis in self.theses
            if thesis.direction == direction
        )

    def by_theme(
        self,
        theme_identifier: str,
    ) -> tuple[InvestmentThesis, ...]:
        """Return theses derived from a specific theme."""

        return tuple(
            thesis
            for thesis in self.theses
            if thesis.source_theme_identifier
            == theme_identifier
        )

    def highest_confidence(self) -> InvestmentThesis:
        """Return the thesis with the highest confidence."""

        return max(
            self.theses,
            key=lambda thesis: thesis.confidence,
        )
