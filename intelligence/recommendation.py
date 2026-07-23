"""Domain models for portfolio recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecommendationLevel(str, Enum):
    """Hierarchy level of a recommendation."""

    MACRO = "macro"
    ASSET_CLASS = "asset_class"
    SECTOR = "sector"
    INDUSTRY = "industry"
    SECURITY = "security"


class RecommendationAction(str, Enum):
    """Recommended portfolio action."""

    OVERWEIGHT = "overweight"
    UNDERWEIGHT = "underweight"
    NEUTRAL = "neutral"
    ACCUMULATE = "accumulate"
    REDUCE = "reduce"
    AVOID = "avoid"


class RecommendationMagnitude(str, Enum):
    """Relative strength of the recommendation."""

    SMALL = "small"
    MODERATE = "moderate"
    LARGE = "large"


class RecommendationStatus(str, Enum):
    """Lifecycle status of a recommendation."""

    ACTIVE = "active"
    WATCH = "watch"
    DEPRECATED = "deprecated"


class ExpectedReturn(str, Enum):
    """Expected relative return profile."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ExpectedRisk(str, Enum):
    """Expected relative risk profile."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass(frozen=True)
class InvestmentRecommendation:
    """
    Standardized investment recommendation.

    Recommendations are generated from investment theses and reviewed
    by the committee. They do not directly execute trades.
    """

    identifier: str
    title: str

    level: RecommendationLevel

    target: str

    action: RecommendationAction
    magnitude: RecommendationMagnitude
    status: RecommendationStatus

    confidence: float

    source_thesis_identifier: str

    rationale: str

    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]

    catalysts: tuple[str, ...]
    risks: tuple[str, ...]

    invalidation_conditions: tuple[str, ...]

    expected_return: ExpectedReturn
    expected_risk: ExpectedRisk

    expected_duration_months: int

    def __post_init__(self) -> None:

        self._require(self.identifier, "identifier")
        self._require(self.title, "title")
        self._require(self.target, "target")
        self._require(
            self.source_thesis_identifier,
            "source_thesis_identifier",
        )
        self._require(self.rationale, "rationale")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        self._require_tuple(
            self.supporting_evidence,
            "supporting_evidence",
            minimum=1,
        )

        self._require_tuple(
            self.contradicting_evidence,
            "contradicting_evidence",
        )

        self._require_tuple(
            self.catalysts,
            "catalysts",
            minimum=1,
        )

        self._require_tuple(
            self.risks,
            "risks",
            minimum=1,
        )

        self._require_tuple(
            self.invalidation_conditions,
            "invalidation_conditions",
            minimum=1,
        )

        if self.expected_duration_months < 1:
            raise ValueError(
                "expected_duration_months must be at least 1"
            )

    @staticmethod
    def _require(
        value: str,
        name: str,
    ) -> None:
        if not value.strip():
            raise ValueError(f"{name} cannot be empty")

    @staticmethod
    def _require_tuple(
        values: tuple[str, ...],
        name: str,
        minimum: int = 0,
    ) -> None:

        if len(values) < minimum:
            raise ValueError(
                f"{name} must contain at least {minimum} item(s)"
            )

        if not all(item.strip() for item in values):
            raise ValueError(
                f"{name} cannot contain empty values"
            )


@dataclass(frozen=True)
class RecommendationSet:
    """
    Collection of portfolio recommendations.
    """

    recommendations: tuple[
        InvestmentRecommendation,
        ...
    ]

    confidence: float

    summary: str

    def __post_init__(self) -> None:

        if not self.recommendations:
            raise ValueError(
                "recommendations cannot be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not self.summary.strip():
            raise ValueError(
                "summary cannot be empty"
            )

        identifiers = [
            recommendation.identifier
            for recommendation in self.recommendations
        ]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError(
                "recommendation identifiers must be unique"
            )

    def by_level(
        self,
        level: RecommendationLevel,
    ) -> tuple[
        InvestmentRecommendation,
        ...
    ]:
        """Return recommendations for one hierarchy level."""

        return tuple(
            recommendation
            for recommendation in self.recommendations
            if recommendation.level == level
        )

    def by_action(
        self,
        action: RecommendationAction,
    ) -> tuple[
        InvestmentRecommendation,
        ...
    ]:
        """Return recommendations with one action."""

        return tuple(
            recommendation
            for recommendation in self.recommendations
            if recommendation.action == action
        )

    def active(
        self,
    ) -> tuple[
        InvestmentRecommendation,
        ...
    ]:
        """Return active recommendations."""

        return tuple(
            recommendation
            for recommendation in self.recommendations
            if recommendation.status
            == RecommendationStatus.ACTIVE
        )

    def highest_confidence(
        self,
    ) -> InvestmentRecommendation:
        """Return the highest-confidence recommendation."""

        return max(
            self.recommendations,
            key=lambda recommendation: recommendation.confidence,
        )
