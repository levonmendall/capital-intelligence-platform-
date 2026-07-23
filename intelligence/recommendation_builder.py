"""Builder for standardized investment recommendations."""

from __future__ import annotations

from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationStatus,
)


class RecommendationBuilder:
    """
    Factory responsible for creating validated InvestmentRecommendation
    instances.

    All recommendation construction should flow through this builder so
    metadata, defaults, and future auditing remain consistent.
    """

    def build(
        self,
        *,
        identifier: str,
        title: str,
        level: RecommendationLevel,
        target: str,
        action: RecommendationAction,
        magnitude: RecommendationMagnitude,
        confidence: float,
        source_thesis_identifier: str,
        rationale: str,
        supporting_evidence: tuple[str, ...],
        contradicting_evidence: tuple[str, ...] = (),
        catalysts: tuple[str, ...],
        risks: tuple[str, ...],
        invalidation_conditions: tuple[str, ...],
        expected_return: ExpectedReturn,
        expected_risk: ExpectedRisk,
        expected_duration_months: int,
        status: RecommendationStatus = RecommendationStatus.ACTIVE,
    ) -> InvestmentRecommendation:
        """Construct a validated investment recommendation."""

        return InvestmentRecommendation(
            identifier=identifier,
            title=title,
            level=level,
            target=target,
            action=action,
            magnitude=magnitude,
            status=status,
            confidence=self._normalize_confidence(confidence),
            source_thesis_identifier=source_thesis_identifier,
            rationale=rationale,
            supporting_evidence=self._clean_tuple(
                supporting_evidence
            ),
            contradicting_evidence=self._clean_tuple(
                contradicting_evidence
            ),
            catalysts=self._clean_tuple(catalysts),
            risks=self._clean_tuple(risks),
            invalidation_conditions=self._clean_tuple(
                invalidation_conditions
            ),
            expected_return=expected_return,
            expected_risk=expected_risk,
            expected_duration_months=expected_duration_months,
        )

    @staticmethod
    def _normalize_confidence(
        confidence: float,
    ) -> float:
        """
        Normalize confidence to four decimal places while ensuring the
        value remains inside the valid range.
        """

        confidence = max(0.0, min(1.0, confidence))
        return round(confidence, 4)

    @staticmethod
    def _clean_tuple(
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        """
        Strip whitespace and remove duplicate entries while preserving
        order.
        """

        cleaned: list[str] = []
        seen: set[str] = set()

        for value in values:
            item = value.strip()

            if not item:
                continue

            if item not in seen:
                cleaned.append(item)
                seen.add(item)

        return tuple(cleaned)
