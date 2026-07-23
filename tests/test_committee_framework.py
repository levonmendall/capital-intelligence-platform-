"""Tests for the shared investment committee decision framework."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from intelligence.committee_adjustment import AdjustmentSet
from intelligence.committee_assessment import CommitteeAssessment
from intelligence.committee_framework import (
    DecisionFramework,
    DecisionThresholds,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
    CommitteeVote,
)


@dataclass(frozen=True)
class StubCommitteeMember:
    """
    Minimal committee participant used to test opinion construction.

    DecisionFramework.build_opinion() only requires the supplied member
    to expose a valid CommitteeRole through its role property.
    """

    role: CommitteeRole = CommitteeRole.MACRO


def make_assessment(
    *,
    base_confidence: float = 0.70,
    adjusted_confidence: float = 0.70,
    rationale: str = "The recommendation is supported by the analysis.",
    strengths: tuple[str, ...] = ("Strong supporting evidence.",),
    concerns: tuple[str, ...] = (),
    suggested_changes: tuple[str, ...] = (),
) -> CommitteeAssessment:
    """
    Build a valid assessment without score adjustments.

    Because the adjustment set is empty, base_confidence and
    adjusted_confidence must be identical.
    """

    if adjusted_confidence != base_confidence:
        raise ValueError(
            "This helper uses an empty AdjustmentSet, so base and "
            "adjusted confidence must be identical."
        )

    return CommitteeAssessment(
        base_confidence=base_confidence,
        adjusted_confidence=adjusted_confidence,
        adjustments=AdjustmentSet(),
        rationale=rationale,
        strengths=strengths,
        concerns=concerns,
        suggested_changes=suggested_changes,
    )


class TestDecisionThresholds:
    """Validation tests for DecisionThresholds."""

    def test_default_thresholds(self) -> None:
        thresholds = DecisionThresholds()

        assert thresholds.strongly_approve == 0.90
        assert thresholds.approve == 0.75
        assert thresholds.neutral == 0.55
        assert thresholds.object == 0.35

    def test_accepts_custom_thresholds(self) -> None:
        thresholds = DecisionThresholds(
            strongly_approve=0.95,
            approve=0.80,
            neutral=0.60,
            object=0.40,
        )

        assert thresholds.strongly_approve == 0.95
        assert thresholds.approve == 0.80
        assert thresholds.neutral == 0.60
        assert thresholds.object == 0.40

    def test_converts_numeric_values_to_float(self) -> None:
        thresholds = DecisionThresholds(
            strongly_approve=1,
            approve=0.8,
            neutral=0.6,
            object=0.4,
        )

        assert thresholds.strongly_approve == 1.0
        assert isinstance(
            thresholds.strongly_approve,
            float,
        )

    @pytest.mark.parametrize(
        "field_name, invalid_value",
        [
            ("strongly_approve", -0.01),
            ("strongly_approve", 1.01),
            ("approve", -0.01),
            ("approve", 1.01),
            ("neutral", -0.01),
            ("neutral", 1.01),
            ("object", -0.01),
            ("object", 1.01),
        ],
    )
    def test_rejects_threshold_outside_valid_range(
        self,
        field_name: str,
        invalid_value: float,
    ) -> None:
        values = {
            "strongly_approve": 0.90,
            "approve": 0.75,
            "neutral": 0.55,
            "object": 0.35,
        }

        values[field_name] = invalid_value

        with pytest.raises(
            ValueError,
            match="between 0.0 and 1.0",
        ):
            DecisionThresholds(**values)

    @pytest.mark.parametrize(
        "field_name, invalid_value",
        [
            ("strongly_approve", "0.90"),
            ("approve", None),
            ("neutral", object()),
            ("object", []),
        ],
    )
    def test_rejects_non_numeric_thresholds(
        self,
        field_name: str,
        invalid_value: object,
    ) -> None:
        values: dict[str, object] = {
            "strongly_approve": 0.90,
            "approve": 0.75,
            "neutral": 0.55,
            "object": 0.35,
        }

        values[field_name] = invalid_value

        with pytest.raises(
            TypeError,
            match="must be numeric",
        ):
            DecisionThresholds(**values)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "field_name, invalid_value",
        [
            ("strongly_approve", float("nan")),
            ("approve", float("inf")),
            ("neutral", float("-inf")),
            ("object", float("nan")),
        ],
    )
    def test_rejects_non_finite_thresholds(
        self,
        field_name: str,
        invalid_value: float,
    ) -> None:
        values = {
            "strongly_approve": 0.90,
            "approve": 0.75,
            "neutral": 0.55,
            "object": 0.35,
        }

        values[field_name] = invalid_value

        with pytest.raises(
            ValueError,
            match="must be finite",
        ):
            DecisionThresholds(**values)

    @pytest.mark.parametrize(
        "thresholds",
        [
            {
                "strongly_approve": 0.75,
                "approve": 0.75,
                "neutral": 0.55,
                "object": 0.35,
            },
            {
                "strongly_approve": 0.90,
                "approve": 0.55,
                "neutral": 0.55,
                "object": 0.35,
            },
            {
                "strongly_approve": 0.90,
                "approve": 0.75,
                "neutral": 0.35,
                "object": 0.35,
            },
            {
                "strongly_approve": 0.75,
                "approve": 0.90,
                "neutral": 0.55,
                "object": 0.35,
            },
        ],
    )
    def test_rejects_unordered_thresholds(
        self,
        thresholds: dict[str, float],
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Thresholds must descend",
        ):
            DecisionThresholds(**thresholds)


class TestDecisionFrameworkInitialization:
    """Initialization and configuration tests."""

    def test_uses_default_thresholds(self) -> None:
        framework = DecisionFramework()

        assert framework.thresholds == DecisionThresholds()

    def test_uses_custom_thresholds(self) -> None:
        thresholds = DecisionThresholds(
            strongly_approve=0.95,
            approve=0.80,
            neutral=0.60,
            object=0.40,
        )

        framework = DecisionFramework(
            thresholds=thresholds
        )

        assert framework.thresholds is thresholds


class TestConfidenceClamping:
    """Tests for confidence normalization."""

    @pytest.mark.parametrize(
        "confidence, expected",
        [
            (-1.0, 0.0),
            (-0.0001, 0.0),
            (0.0, 0.0),
            (0.123456, 0.1235),
            (0.50, 0.50),
            (0.99999, 1.0),
            (1.0, 1.0),
            (1.0001, 1.0),
            (2.0, 1.0),
        ],
    )
    def test_clamps_and_rounds_confidence(
        self,
        confidence: float,
        expected: float,
    ) -> None:
        assert (
            DecisionFramework.clamp(confidence)
            == expected
        )

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "0.75",
            None,
            object(),
            [],
            {},
        ],
    )
    def test_rejects_non_numeric_confidence(
        self,
        invalid_value: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match="confidence must be numeric",
        ):
            DecisionFramework.clamp(  # type: ignore[arg-type]
                invalid_value
            )

    @pytest.mark.parametrize(
        "invalid_value",
        [
            float("nan"),
            float("inf"),
            float("-inf"),
        ],
    )
    def test_rejects_non_finite_confidence(
        self,
        invalid_value: float,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="confidence must be finite",
        ):
            DecisionFramework.clamp(
                invalid_value
            )


class TestVoteCalculation:
    """Boundary and classification tests for committee votes."""

    @pytest.mark.parametrize(
        "confidence, expected_vote",
        [
            (1.00, CommitteeVote.STRONGLY_APPROVE),
            (0.95, CommitteeVote.STRONGLY_APPROVE),
            (0.90, CommitteeVote.STRONGLY_APPROVE),
            (0.8999, CommitteeVote.APPROVE),
            (0.80, CommitteeVote.APPROVE),
            (0.75, CommitteeVote.APPROVE),
            (0.7499, CommitteeVote.NEUTRAL),
            (0.60, CommitteeVote.NEUTRAL),
            (0.55, CommitteeVote.NEUTRAL),
            (0.5499, CommitteeVote.OBJECT),
            (0.40, CommitteeVote.OBJECT),
            (0.35, CommitteeVote.OBJECT),
            (0.3499, CommitteeVote.STRONGLY_OBJECT),
            (0.00, CommitteeVote.STRONGLY_OBJECT),
        ],
    )
    def test_default_vote_boundaries(
        self,
        confidence: float,
        expected_vote: CommitteeVote,
    ) -> None:
        framework = DecisionFramework()

        assert (
            framework.vote(confidence)
            == expected_vote
        )

    def test_vote_clamps_confidence_before_classification(
        self,
    ) -> None:
        framework = DecisionFramework()

        assert (
            framework.vote(2.0)
            == CommitteeVote.STRONGLY_APPROVE
        )

        assert (
            framework.vote(-2.0)
            == CommitteeVote.STRONGLY_OBJECT
        )

    @pytest.mark.parametrize(
        "confidence, expected_vote",
        [
            (0.95, CommitteeVote.STRONGLY_APPROVE),
            (0.9499, CommitteeVote.APPROVE),
            (0.80, CommitteeVote.APPROVE),
            (0.7999, CommitteeVote.NEUTRAL),
            (0.60, CommitteeVote.NEUTRAL),
            (0.5999, CommitteeVote.OBJECT),
            (0.40, CommitteeVote.OBJECT),
            (0.3999, CommitteeVote.STRONGLY_OBJECT),
        ],
    )
    def test_custom_vote_boundaries(
        self,
        confidence: float,
        expected_vote: CommitteeVote,
    ) -> None:
        framework = DecisionFramework(
            thresholds=DecisionThresholds(
                strongly_approve=0.95,
                approve=0.80,
                neutral=0.60,
                object=0.40,
            )
        )

        assert (
            framework.vote(confidence)
            == expected_vote
        )


class TestConfidenceBands:
    """Tests for human-readable confidence classifications."""

    @pytest.mark.parametrize(
        "confidence, expected_band",
        [
            (1.00, "Very High"),
            (0.90, "Very High"),
            (0.8999, "High"),
            (0.75, "High"),
            (0.7499, "Moderate"),
            (0.55, "Moderate"),
            (0.5499, "Low"),
            (0.35, "Low"),
            (0.3499, "Very Low"),
            (0.00, "Very Low"),
        ],
    )
    def test_default_confidence_bands(
        self,
        confidence: float,
        expected_band: str,
    ) -> None:
        framework = DecisionFramework()

        assert (
            framework.confidence_band(confidence)
            == expected_band
        )


class TestOpinionConstruction:
    """Tests for standardized CommitteeOpinion creation."""

    def test_builds_committee_opinion(self) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember(
            role=CommitteeRole.MACRO
        )
        assessment = make_assessment(
            base_confidence=0.80,
            adjusted_confidence=0.80,
            rationale=(
                "The macro environment supports the recommendation."
            ),
            strengths=(
                "Economic conditions are supportive.",
                "The horizon matches the thesis.",
            ),
            concerns=(
                "Policy uncertainty remains.",
            ),
            suggested_changes=(
                "Reduce position size if volatility rises.",
            ),
        )

        opinion = framework.build_opinion(
            recommendation_identifier="REC-001",
            member=member,  # type: ignore[arg-type]
            assessment=assessment,
        )

        assert isinstance(
            opinion,
            CommitteeOpinion,
        )
        assert (
            opinion.recommendation_identifier
            == "REC-001"
        )
        assert opinion.member == CommitteeRole.MACRO
        assert opinion.vote == CommitteeVote.APPROVE
        assert opinion.confidence == 0.80
        assert (
            opinion.rationale
            == assessment.rationale
        )
        assert (
            opinion.strengths
            == assessment.strengths
        )
        assert (
            opinion.concerns
            == assessment.concerns
        )
        assert (
            opinion.suggested_changes
            == assessment.suggested_changes
        )

    def test_strips_recommendation_identifier(
        self,
    ) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember()
        assessment = make_assessment()

        opinion = framework.build_opinion(
            recommendation_identifier="  REC-002  ",
            member=member,  # type: ignore[arg-type]
            assessment=assessment,
        )

        assert (
            opinion.recommendation_identifier
            == "REC-002"
        )

    def test_uses_adjusted_confidence_for_vote(
        self,
    ) -> None:
        """
        This test uses a valid non-empty adjustment set to prove that
        opinion construction uses final adjusted confidence rather than
        base confidence.
        """

        from intelligence.committee_adjustment import (
            AdjustmentCategory,
            ScoreAdjustment,
        )

        adjustment = ScoreAdjustment(
            category=AdjustmentCategory.ECONOMIC,
            description="Supportive macro conditions.",
            raw_value=0.20,
            applied_value=0.20,
        )

        assessment = CommitteeAssessment(
            base_confidence=0.70,
            adjusted_confidence=0.90,
            adjustments=AdjustmentSet(
                adjustments=(adjustment,)
            ),
            rationale=(
                "Macro conditions materially improve conviction."
            ),
            strengths=(
                "Strong economic alignment.",
            ),
            concerns=(),
            suggested_changes=(),
        )

        framework = DecisionFramework()
        member = StubCommitteeMember()

        opinion = framework.build_opinion(
            recommendation_identifier="REC-003",
            member=member,  # type: ignore[arg-type]
            assessment=assessment,
        )

        assert opinion.confidence == 0.90
        assert (
            opinion.vote
            == CommitteeVote.STRONGLY_APPROVE
        )

    def test_rejects_non_string_identifier(
        self,
    ) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember()
        assessment = make_assessment()

        with pytest.raises(
            TypeError,
            match=(
                "recommendation_identifier must be a string"
            ),
        ):
            framework.build_opinion(
                recommendation_identifier=123,  # type: ignore[arg-type]
                member=member,  # type: ignore[arg-type]
                assessment=assessment,
            )

    def test_rejects_blank_identifier(self) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember()
        assessment = make_assessment()

        with pytest.raises(
            ValueError,
            match=(
                "recommendation_identifier cannot be empty"
            ),
        ):
            framework.build_opinion(
                recommendation_identifier="   ",
                member=member,  # type: ignore[arg-type]
                assessment=assessment,
            )

    def test_rejects_invalid_assessment(self) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember()

        with pytest.raises(
            TypeError,
            match=(
                "assessment must be a CommitteeAssessment"
            ),
        ):
            framework.build_opinion(
                recommendation_identifier="REC-004",
                member=member,  # type: ignore[arg-type]
                assessment="invalid",  # type: ignore[arg-type]
            )

    def test_rejects_invalid_member_role(self) -> None:
        @dataclass(frozen=True)
        class InvalidMember:
            role: str = "macro"

        framework = DecisionFramework()
        assessment = make_assessment()

        with pytest.raises(
            TypeError,
            match=(
                "member.role must be a CommitteeRole"
            ),
        ):
            framework.build_opinion(
                recommendation_identifier="REC-005",
                member=InvalidMember(),  # type: ignore[arg-type]
                assessment=assessment,
            )


class TestFrameworkSummaries:
    """Tests for deterministic governance summaries."""

    def test_summarizes_assessment(self) -> None:
        framework = DecisionFramework()

        assessment = make_assessment(
            base_confidence=0.80,
            adjusted_confidence=0.80,
            strengths=(
                "Strong evidence.",
                "Suitable duration.",
            ),
            concerns=(
                "Execution risk.",
            ),
            suggested_changes=(
                "Use a smaller initial allocation.",
            ),
        )

        summary = framework.summarize(
            assessment
        )

        assert summary == (
            "approve | "
            "Base 80.00% | "
            "Adjustment +0.00% | "
            "Final 80.00% | "
            "2 strengths | "
            "1 concerns | "
            "1 changes"
        )

    def test_summary_is_deterministic(self) -> None:
        framework = DecisionFramework()
        assessment = make_assessment(
            base_confidence=0.60,
            adjusted_confidence=0.60,
        )

        first = framework.summarize(
            assessment
        )
        second = framework.summarize(
            assessment
        )

        assert first == second

    def test_summary_uses_custom_thresholds(
        self,
    ) -> None:
        framework = DecisionFramework(
            thresholds=DecisionThresholds(
                strongly_approve=0.95,
                approve=0.85,
                neutral=0.65,
                object=0.45,
            )
        )

        assessment = make_assessment(
            base_confidence=0.80,
            adjusted_confidence=0.80,
        )

        summary = framework.summarize(
            assessment
        )

        assert summary.startswith(
            "neutral |"
        )

    def test_rejects_invalid_summary_input(
        self,
    ) -> None:
        framework = DecisionFramework()

        with pytest.raises(
            TypeError,
            match=(
                "assessment must be a CommitteeAssessment"
            ),
        ):
            framework.summarize(
                "invalid"  # type: ignore[arg-type]
            )


class TestFrameworkDeterminism:
    """Additional contract tests for repeatable framework behavior."""

    def test_repeated_vote_calls_return_same_result(
        self,
    ) -> None:
        framework = DecisionFramework()

        results = tuple(
            framework.vote(0.812345)
            for _ in range(10)
        )

        assert results == (
            CommitteeVote.APPROVE,
        ) * 10

    def test_repeated_opinion_builds_are_equal(
        self,
    ) -> None:
        framework = DecisionFramework()
        member = StubCommitteeMember()
        assessment = make_assessment(
            base_confidence=0.78,
            adjusted_confidence=0.78,
        )

        first = framework.build_opinion(
            recommendation_identifier="REC-006",
            member=member,  # type: ignore[arg-type]
            assessment=assessment,
        )

        second = framework.build_opinion(
            recommendation_identifier="REC-006",
            member=member,  # type: ignore[arg-type]
            assessment=assessment,
        )

        assert first == second
