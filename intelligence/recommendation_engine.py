"""Engine for generating standardized investment recommendations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from intelligence.recommendation import (
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationSet,
    RecommendationStatus,
)
from intelligence.recommendation_rules import RecommendationRules
from intelligence.thesis import InvestmentThesisSet


class RecommendationEngine:
    """
    Convert an InvestmentThesisSet into a RecommendationSet.

    The engine coordinates recommendation rules, merges overlapping
    recommendations, calculates aggregate confidence, imposes deterministic
    ordering, and produces an executive summary.

    Investment logic belongs in RecommendationRules rather than this class.
    """

    _MAGNITUDE_WEIGHTS: dict[RecommendationMagnitude, float] = {
        RecommendationMagnitude.SMALL: 0.75,
        RecommendationMagnitude.MODERATE: 1.00,
        RecommendationMagnitude.LARGE: 1.50,
    }

    _MAGNITUDE_PRECEDENCE: dict[RecommendationMagnitude, int] = {
        RecommendationMagnitude.SMALL: 0,
        RecommendationMagnitude.MODERATE: 1,
        RecommendationMagnitude.LARGE: 2,
    }

    _LEVEL_PRECEDENCE: dict[RecommendationLevel, int] = {
        RecommendationLevel.MACRO: 0,
        RecommendationLevel.ASSET_CLASS: 1,
        RecommendationLevel.SECTOR: 2,
        RecommendationLevel.INDUSTRY: 3,
        RecommendationLevel.SECURITY: 4,
    }

    _STATUS_PRECEDENCE: dict[RecommendationStatus, int] = {
        RecommendationStatus.ACTIVE: 2,
        RecommendationStatus.WATCH: 1,
        RecommendationStatus.DEPRECATED: 0,
    }

    def __init__(
        self,
        rules: RecommendationRules | None = None,
    ) -> None:
        self._rules = rules or RecommendationRules()

    def generate(
        self,
        thesis_set: InvestmentThesisSet,
    ) -> RecommendationSet:
        """
        Generate a deterministic RecommendationSet.

        Raises:
            TypeError: If thesis_set is not an InvestmentThesisSet.
            ValueError: If no actionable recommendations can be generated.
        """

        self._validate(thesis_set)

        generated = self._generate_from_theses(thesis_set)

        if not generated:
            raise ValueError(
                "No recommendations were generated from the thesis set"
            )

        merged = self._merge_duplicates(generated)
        ordered = self._sort_recommendations(merged)
        confidence = self._weighted_confidence(ordered)
        summary = self._build_summary(
            recommendations=ordered,
            confidence=confidence,
        )

        return RecommendationSet(
            recommendations=ordered,
            confidence=confidence,
            summary=summary,
        )

    @staticmethod
    def _validate(
        thesis_set: InvestmentThesisSet,
    ) -> None:
        if not isinstance(thesis_set, InvestmentThesisSet):
            raise TypeError(
                "thesis_set must be an InvestmentThesisSet"
            )

    def _generate_from_theses(
        self,
        thesis_set: InvestmentThesisSet,
    ) -> tuple[InvestmentRecommendation, ...]:
        generated: list[InvestmentRecommendation] = []

        for thesis in thesis_set.theses:
            generated.extend(self._rules.apply(thesis))

        return tuple(generated)

    def _merge_duplicates(
        self,
        recommendations: tuple[InvestmentRecommendation, ...],
    ) -> tuple[InvestmentRecommendation, ...]:
        """
        Merge recommendations with the same portfolio meaning.

        Recommendations are considered duplicates when level, target, and
        action are identical. Their evidence, catalysts, risks, invalidation
        conditions, and source thesis identifiers are combined.
        """

        grouped: dict[
            tuple[
                RecommendationLevel,
                str,
                RecommendationAction,
            ],
            list[InvestmentRecommendation],
        ] = {}

        for recommendation in recommendations:
            key = (
                recommendation.level,
                recommendation.target,
                recommendation.action,
            )

            grouped.setdefault(key, []).append(recommendation)

        merged = [
            self._merge_group(group)
            for group in grouped.values()
        ]

        return tuple(merged)

    def _merge_group(
        self,
        recommendations: list[InvestmentRecommendation],
    ) -> InvestmentRecommendation:
        if not recommendations:
            raise ValueError(
                "Cannot merge an empty recommendation group"
            )

        if len(recommendations) == 1:
            return recommendations[0]

        ordered = sorted(
            recommendations,
            key=lambda recommendation: (
                -recommendation.confidence,
                recommendation.identifier,
            ),
        )

        anchor = ordered[0]

        return InvestmentRecommendation(
            identifier=self._select_identifier(ordered),
            title=anchor.title,
            level=anchor.level,
            target=anchor.target,
            action=anchor.action,
            magnitude=self._strongest_magnitude(ordered),
            status=self._strongest_status(ordered),
            confidence=self._weighted_confidence(
                tuple(ordered)
            ),
            source_thesis_identifier=(
                self._merge_source_identifiers(ordered)
            ),
            rationale=self._merge_rationales(ordered),
            supporting_evidence=self._merge_text_values(
                recommendation.supporting_evidence
                for recommendation in ordered
            ),
            contradicting_evidence=self._merge_text_values(
                recommendation.contradicting_evidence
                for recommendation in ordered
            ),
            catalysts=self._merge_text_values(
                recommendation.catalysts
                for recommendation in ordered
            ),
            risks=self._merge_text_values(
                recommendation.risks
                for recommendation in ordered
            ),
            invalidation_conditions=self._merge_text_values(
                recommendation.invalidation_conditions
                for recommendation in ordered
            ),
            expected_return=anchor.expected_return,
            expected_risk=anchor.expected_risk,
            expected_duration_months=(
                self._weighted_duration(ordered)
            ),
        )

    @staticmethod
    def _select_identifier(
        recommendations: list[InvestmentRecommendation],
    ) -> str:
        """
        Preserve the highest-confidence recommendation identifier.

        Identifiers remain stable because the input list is ordered by
        confidence descending and identifier ascending.
        """

        return recommendations[0].identifier

    def _strongest_magnitude(
        self,
        recommendations: list[InvestmentRecommendation],
    ) -> RecommendationMagnitude:
        return max(
            (
                recommendation.magnitude
                for recommendation in recommendations
            ),
            key=lambda magnitude: (
                self._MAGNITUDE_PRECEDENCE[magnitude]
            ),
        )

    def _strongest_status(
        self,
        recommendations: list[InvestmentRecommendation],
    ) -> RecommendationStatus:
        return max(
            (
                recommendation.status
                for recommendation in recommendations
            ),
            key=lambda status: self._STATUS_PRECEDENCE[status],
        )

    @staticmethod
    def _merge_source_identifiers(
        recommendations: list[InvestmentRecommendation],
    ) -> str:
        identifiers: list[str] = []

        for recommendation in recommendations:
            for identifier in (
                recommendation.source_thesis_identifier.split(",")
            ):
                cleaned = identifier.strip()

                if cleaned and cleaned not in identifiers:
                    identifiers.append(cleaned)

        return ", ".join(sorted(identifiers))

    @staticmethod
    def _merge_rationales(
        recommendations: list[InvestmentRecommendation],
    ) -> str:
        rationales: list[str] = []

        for recommendation in recommendations:
            rationale = recommendation.rationale.strip()

            if rationale and rationale not in rationales:
                rationales.append(rationale)

        return " ".join(rationales)

    @staticmethod
    def _merge_text_values(
        groups: Iterable[tuple[str, ...]],
    ) -> tuple[str, ...]:
        merged: list[str] = []
        seen: set[str] = set()

        for values in groups:
            for value in values:
                cleaned = value.strip()

                if not cleaned:
                    continue

                normalized = cleaned.casefold()

                if normalized in seen:
                    continue

                seen.add(normalized)
                merged.append(cleaned)

        return tuple(merged)

    def _weighted_confidence(
        self,
        recommendations: tuple[InvestmentRecommendation, ...],
    ) -> float:
        if not recommendations:
            raise ValueError(
                "Cannot calculate confidence without recommendations"
            )

        weighted_total = 0.0
        total_weight = 0.0

        for recommendation in recommendations:
            weight = self._MAGNITUDE_WEIGHTS[
                recommendation.magnitude
            ]

            weighted_total += recommendation.confidence * weight
            total_weight += weight

        return round(weighted_total / total_weight, 4)

    def _weighted_duration(
        self,
        recommendations: list[InvestmentRecommendation],
    ) -> int:
        weighted_total = 0.0
        total_weight = 0.0

        for recommendation in recommendations:
            weight = self._MAGNITUDE_WEIGHTS[
                recommendation.magnitude
            ]

            weighted_total += (
                recommendation.expected_duration_months
                * weight
            )
            total_weight += weight

        return max(1, round(weighted_total / total_weight))

    def _sort_recommendations(
        self,
        recommendations: tuple[InvestmentRecommendation, ...],
    ) -> tuple[InvestmentRecommendation, ...]:
        return tuple(
            sorted(
                recommendations,
                key=lambda recommendation: (
                    self._LEVEL_PRECEDENCE[
                        recommendation.level
                    ],
                    -recommendation.confidence,
                    recommendation.target.casefold(),
                    recommendation.identifier.casefold(),
                ),
            )
        )

    def _build_summary(
        self,
        *,
        recommendations: tuple[InvestmentRecommendation, ...],
        confidence: float,
    ) -> str:
        level_counts = Counter(
            recommendation.level
            for recommendation in recommendations
        )

        action_counts = Counter(
            recommendation.action
            for recommendation in recommendations
        )

        highest = max(
            recommendations,
            key=lambda recommendation: (
                recommendation.confidence,
                self._MAGNITUDE_PRECEDENCE[
                    recommendation.magnitude
                ],
                recommendation.title,
            ),
        )

        return "\n".join(
            (
                "Recommendation Summary",
                "",
                f"Total Recommendations: {len(recommendations)}",
                "",
                "Recommendation Levels",
                (
                    "Macro: "
                    f"{level_counts[RecommendationLevel.MACRO]}"
                ),
                (
                    "Asset Class: "
                    f"{level_counts[RecommendationLevel.ASSET_CLASS]}"
                ),
                (
                    "Sector: "
                    f"{level_counts[RecommendationLevel.SECTOR]}"
                ),
                (
                    "Industry: "
                    f"{level_counts[RecommendationLevel.INDUSTRY]}"
                ),
                (
                    "Security: "
                    f"{level_counts[RecommendationLevel.SECURITY]}"
                ),
                "",
                "Allocation Tilt",
                (
                    "Overweight: "
                    f"{action_counts[RecommendationAction.OVERWEIGHT]}"
                ),
                (
                    "Underweight: "
                    f"{action_counts[RecommendationAction.UNDERWEIGHT]}"
                ),
                (
                    "Accumulate: "
                    f"{action_counts[RecommendationAction.ACCUMULATE]}"
                ),
                (
                    "Reduce: "
                    f"{action_counts[RecommendationAction.REDUCE]}"
                ),
                (
                    "Avoid: "
                    f"{action_counts[RecommendationAction.AVOID]}"
                ),
                (
                    "Neutral: "
                    f"{action_counts[RecommendationAction.NEUTRAL]}"
                ),
                "",
                "Highest Conviction",
                (
                    f"{highest.title}: "
                    f"{highest.confidence:.1%}"
                ),
                "",
                (
                    "Overall Recommendation Confidence: "
                    f"{confidence:.1%}"
                ),
            )
        )
