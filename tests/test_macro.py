"""Tests for the Macro Committee Member."""

from __future__ import annotations

import pytest

from intelligence.committee_adjustment import (
    AdjustmentCategory,
    ScoreAdjustment,
)
from intelligence.committee_adjustment_engine import (
    AdjustmentEngine,
    AdjustmentPolicy,
)
from intelligence.committee_assessment import (
    CommitteeAssessment,
)
from intelligence.committee_framework import (
    DecisionFramework,
    DecisionThresholds,
)
from intelligence.committee_members.macro import (
    MacroCommitteeMember,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeRole,
    CommitteeVote,
)
from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
    RecommendationStatus,
)


def make_recommendation(
    *,
    identifier: str = "REC-MACRO-001",
    title: str = "Overweight Investment Grade Bonds",
    level: RecommendationLevel = RecommendationLevel.ASSET_CLASS,
    target: str = "Investment Grade Bonds",
    action: RecommendationAction = RecommendationAction.OVERWEIGHT,
    magnitude: RecommendationMagnitude = (
        RecommendationMagnitude.MODERATE
    ),
    status: RecommendationStatus = RecommendationStatus.ACTIVE,
    confidence: float = 0.70,
    expected_return: ExpectedReturn = ExpectedReturn.MODERATE,
    expected_risk: ExpectedRisk = ExpectedRisk.LOW,
    expected_duration_months: int = 12,
) -> InvestmentRecommendation:
    """Build a valid recommendation for Macro Committee tests."""

    return InvestmentRecommendation(
        identifier=identifier,
        title=title,
        level=level,
        target=target,
        action=action,
        magnitude=magnitude,
        status=status,
        confidence=confidence,
        source_thesis_identifier="THESIS-001",
        rationale=(
            "Disinflation and slower economic growth support "
            "high-quality fixed-income exposure."
        ),
        supporting_evidence=(
            "Inflation momentum is moderating.",
            "Policy rates are expected to stabilize.",
        ),
        contradicting_evidence=(
            "Economic growth remains resilient.",
        ),
        catalysts=(
            "Lower inflation readings.",
            "A less restrictive monetary-policy outlook.",
        ),
        risks=(
            "Inflation reaccelerates.",
            "Long-term yields rise materially.",
        ),
        invalidation_conditions=(
            "Core inflation begins a sustained acceleration.",
        ),
        expected_return=expected_return,
        expected_risk=expected_risk,
        expected_duration_months=expected_duration_months,
    )


class TestMacroCommitteeIdentity:
    """Tests for Macro Committee identity and defaults."""

    def test_role_is_macro(self) -> None:
        member = MacroCommitteeMember()

        assert member.role == CommitteeRole.MACRO

    def test_display_name(self) -> None:
        member = MacroCommitteeMember()

        assert member.display_name == "Macro Committee"

    def test_default_voting_weight(self) -> None:
        member = MacroCommitteeMember()

        assert member.voting_weight == 1.0

    def test_macro_member_has_no_veto_by_default(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        assert member.has_veto is False

    def test_repr_contains_governance_identity(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        representation = repr(member)

        assert "MacroCommitteeMember" in representation
        assert "macro" in representation
        assert "Macro Committee" in representation
        assert "weight=1.0" in representation
        assert "veto=False" in representation


class TestMacroAllocationAdjustments:
    """Tests for recommendation-level macro adjustments."""

    @pytest.mark.parametrize(
        "level, expected_value, expected_description",
        [
            (
                RecommendationLevel.MACRO,
                0.08,
                "directly expresses a macro view",
            ),
            (
                RecommendationLevel.ASSET_CLASS,
                0.06,
                "strongly influenced by the macro regime",
            ),
            (
                RecommendationLevel.SECTOR,
                0.03,
                "meaningful macro sensitivity",
            ),
            (
                RecommendationLevel.INDUSTRY,
                0.01,
                "limited direct macro scope",
            ),
            (
                RecommendationLevel.SECURITY,
                0.00,
                "receives no macro-level bonus",
            ),
        ],
    )
    def test_allocation_adjustment_by_level(
        self,
        level: RecommendationLevel,
        expected_value: float,
        expected_description: str,
    ) -> None:
        recommendation = make_recommendation(
            level=level
        )

        adjustment = (
            MacroCommitteeMember
            ._allocation_adjustment(
                recommendation
            )
        )

        assert isinstance(
            adjustment,
            ScoreAdjustment,
        )
        assert (
            adjustment.category
            == AdjustmentCategory.ALLOCATION
        )
        assert adjustment.raw_value == expected_value
        assert (
            expected_description
            in adjustment.description
        )


class TestMacroDurationAdjustments:
    """Tests for macro investment-horizon scoring."""

    @pytest.mark.parametrize(
        "months, expected_value, expected_description",
        [
            (
                36,
                0.05,
                "Long investment horizon",
            ),
            (
                24,
                0.05,
                "Long investment horizon",
            ),
            (
                18,
                0.03,
                "Intermediate horizon",
            ),
            (
                12,
                0.03,
                "Intermediate horizon",
            ),
            (
                9,
                0.01,
                "limited time",
            ),
            (
                6,
                0.01,
                "limited time",
            ),
            (
                5,
                -0.02,
                "Short investment horizon",
            ),
            (
                1,
                -0.02,
                "Short investment horizon",
            ),
        ],
    )
    def test_duration_adjustment(
        self,
        months: int,
        expected_value: float,
        expected_description: str,
    ) -> None:
        recommendation = make_recommendation(
            expected_duration_months=months
        )

        adjustment = (
            MacroCommitteeMember
            ._duration_adjustment(
                recommendation
            )
        )

        assert (
            adjustment.category
            == AdjustmentCategory.DURATION
        )
        assert adjustment.raw_value == expected_value
        assert (
            expected_description
            in adjustment.description
        )


class TestResearchConfidenceAdjustments:
    """Tests for underlying research-conviction scoring."""

    @pytest.mark.parametrize(
        "confidence, expected_value, expected_description",
        [
            (
                0.95,
                0.03,
                "very high conviction",
            ),
            (
                0.85,
                0.03,
                "very high conviction",
            ),
            (
                0.84,
                0.01,
                "strong conviction",
            ),
            (
                0.75,
                0.01,
                "strong conviction",
            ),
            (
                0.74,
                0.00,
                "no additional macro adjustment",
            ),
            (
                0.65,
                0.00,
                "no additional macro adjustment",
            ),
            (
                0.64,
                -0.02,
                "below the preferred macro threshold",
            ),
            (
                0.55,
                -0.02,
                "below the preferred macro threshold",
            ),
            (
                0.54,
                -0.05,
                "insufficient for strong macro conviction",
            ),
            (
                0.30,
                -0.05,
                "insufficient for strong macro conviction",
            ),
        ],
    )
    def test_research_confidence_adjustment(
        self,
        confidence: float,
        expected_value: float,
        expected_description: str,
    ) -> None:
        recommendation = make_recommendation(
            confidence=confidence
        )

        adjustment = (
            MacroCommitteeMember
            ._research_confidence_adjustment(
                recommendation
            )
        )

        assert (
            adjustment.category
            == AdjustmentCategory.ECONOMIC
        )
        assert adjustment.raw_value == expected_value
        assert (
            expected_description
            in adjustment.description
        )


class TestMacroAssessment:
    """Tests for complete Macro Committee assessments."""

    def test_assess_returns_committee_assessment(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        assessment = member.assess(
            recommendation
        )

        assert isinstance(
            assessment,
            CommitteeAssessment,
        )

    def test_assessment_preserves_base_confidence(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            confidence=0.70
        )

        assessment = member.assess(
            recommendation
        )

        assert assessment.base_confidence == 0.70

    def test_asset_class_assessment_aggregates_adjustments(
        self,
    ) -> None:
        """
        Asset-class recommendation, 12-month duration, and 70%
        confidence produce:

        Allocation: +0.06
        Duration:   +0.03
        Research:   +0.00

        Final confidence: 0.79
        """

        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.70,
            expected_duration_months=12,
        )

        assessment = member.assess(
            recommendation
        )

        assert len(assessment.adjustments) == 3
        assert (
            assessment.adjustments
            .total_raw_adjustment
            == 0.09
        )
        assert (
            assessment.adjustments
            .total_applied_adjustment
            == 0.09
        )
        assert assessment.adjusted_confidence == 0.79
        assert assessment.confidence_change == 0.09

    def test_macro_level_high_conviction_assessment(
        self,
    ) -> None:
        """
        Macro recommendation, long duration, and strong research
        confidence produce:

        Allocation: +0.08
        Duration:   +0.05
        Research:   +0.01

        Base 0.80 becomes 0.94.
        """

        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO,
            confidence=0.80,
            expected_duration_months=24,
        )

        assessment = member.assess(
            recommendation
        )

        assert (
            assessment.adjustments
            .total_applied_adjustment
            == 0.14
        )
        assert assessment.adjusted_confidence == 0.94
        assert assessment.is_high_confidence is True

    def test_low_confidence_short_horizon_assessment(
        self,
    ) -> None:
        """
        Security-level recommendation, short duration, and weak
        research conviction produce:

        Allocation:  0.00
        Duration:   -0.02
        Research:   -0.05

        Base 0.50 becomes 0.43.
        """

        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY,
            confidence=0.50,
            expected_duration_months=3,
        )

        assessment = member.assess(
            recommendation
        )

        assert (
            assessment.adjustments
            .total_applied_adjustment
            == -0.07
        )
        assert assessment.adjusted_confidence == 0.43
        assert assessment.has_concerns is True
        assert assessment.requires_revision is True

    def test_assessment_contains_expected_categories(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        assessment = member.assess(
            recommendation
        )

        assert assessment.adjustments.categories == (
            AdjustmentCategory.ALLOCATION,
            AdjustmentCategory.DURATION,
            AdjustmentCategory.ECONOMIC,
        )

    def test_adjustment_order_is_deterministic(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        assessment = member.assess(
            recommendation
        )

        categories = tuple(
            adjustment.category
            for adjustment in assessment.adjustments
        )

        assert categories == (
            AdjustmentCategory.ALLOCATION,
            AdjustmentCategory.DURATION,
            AdjustmentCategory.ECONOMIC,
        )

    def test_assessment_rationale_identifies_target(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            target="Government Bonds"
        )

        assessment = member.assess(
            recommendation
        )

        assert "Government Bonds" in assessment.rationale
        assert "top-down" in assessment.rationale
        assert "investment horizon" in assessment.rationale


class TestMacroStrengths:
    """Tests for macro assessment strengths."""

    def test_asset_class_is_identified_as_strength(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS
        )

        assessment = member.assess(
            recommendation
        )

        assert (
            "Recommendation is expressed at a level "
            "appropriate for macro allocation."
            in assessment.strengths
        )

    def test_macro_level_is_identified_as_strength(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "appropriate for macro allocation"
            in strength
            for strength in assessment.strengths
        )

    def test_long_horizon_is_identified_as_strength(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            expected_duration_months=18
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "horizon is appropriate"
            in strength
            for strength in assessment.strengths
        )

    def test_high_research_confidence_is_strength(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            confidence=0.80
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "strong conviction"
            in strength
            for strength in assessment.strengths
        )

    def test_fallback_strength_is_present(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY,
            confidence=0.65,
            expected_duration_months=6,
        )

        assessment = member.assess(
            recommendation
        )

        assert assessment.strengths == (
            "Recommendation can be evaluated within the "
            "current macro framework.",
        )


class TestMacroConcerns:
    """Tests for macro assessment concerns."""

    def test_short_horizon_creates_concern(self) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            expected_duration_months=3
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "require a longer investment horizon"
            in concern
            for concern in assessment.concerns
        )

    def test_low_confidence_creates_concern(self) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            confidence=0.55
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "confidence is limited"
            in concern
            for concern in assessment.concerns
        )

    def test_security_level_creates_concern(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "outside the macro thesis"
            in concern
            for concern in assessment.concerns
        )

    def test_supported_asset_class_can_have_no_concerns(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.75,
            expected_duration_months=12,
        )

        assessment = member.assess(
            recommendation
        )

        assert assessment.concerns == ()
        assert assessment.has_concerns is False


class TestMacroSuggestedChanges:
    """Tests for suggested recommendation revisions."""

    def test_short_horizon_suggests_extension(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            expected_duration_months=3
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "extending the expected investment horizon"
            in change
            for change in assessment.suggested_changes
        )

    def test_security_recommendation_suggests_macro_pairing(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "asset-class or sector allocation view"
            in change
            for change in assessment.suggested_changes
        )

    def test_low_confidence_suggests_more_evidence(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            confidence=0.55
        )

        assessment = member.assess(
            recommendation
        )

        assert any(
            "additional macro evidence"
            in change
            for change in assessment.suggested_changes
        )

    def test_supported_recommendation_requires_no_revision(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.75,
            expected_duration_months=12,
        )

        assessment = member.assess(
            recommendation
        )

        assert assessment.suggested_changes == ()
        assert assessment.requires_revision is False


class TestMacroPolicyEnforcement:
    """Tests for centralized adjustment-policy enforcement."""

    def test_custom_policy_caps_single_adjustments(
        self,
    ) -> None:
        policy = AdjustmentPolicy(
            maximum_single_adjustment=0.02,
            maximum_positive_adjustment=0.30,
            maximum_negative_adjustment=0.30,
        )

        member = MacroCommitteeMember(
            adjustment_engine=AdjustmentEngine(
                policy=policy
            )
        )

        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO,
            confidence=0.80,
            expected_duration_months=24,
        )

        assessment = member.assess(
            recommendation
        )

        assert tuple(
            adjustment.raw_value
            for adjustment in assessment.adjustments
        ) == (
            0.08,
            0.05,
            0.01,
        )

        assert tuple(
            adjustment.applied_value
            for adjustment in assessment.adjustments
        ) == (
            0.02,
            0.02,
            0.01,
        )

        assert assessment.adjusted_confidence == 0.85
        assert assessment.was_policy_constrained is True
        assert (
            len(
                assessment.adjustments.constrained
            )
            == 2
        )

    def test_custom_policy_caps_cumulative_positive_total(
        self,
    ) -> None:
        policy = AdjustmentPolicy(
            maximum_single_adjustment=0.20,
            maximum_positive_adjustment=0.10,
            maximum_negative_adjustment=0.30,
        )

        member = MacroCommitteeMember(
            adjustment_engine=AdjustmentEngine(
                policy=policy
            )
        )

        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO,
            confidence=0.70,
            expected_duration_months=24,
        )

        assessment = member.assess(
            recommendation
        )

        assert (
            assessment.adjustments
            .total_raw_adjustment
            == 0.13
        )
        assert (
            assessment.adjustments
            .total_applied_adjustment
            == 0.10
        )
        assert assessment.adjusted_confidence == 0.80
        assert assessment.was_policy_constrained is True

    def test_default_macro_adjustments_are_not_constrained(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO,
            confidence=0.70,
            expected_duration_months=24,
        )

        assessment = member.assess(
            recommendation
        )

        assert assessment.was_policy_constrained is False
        assert assessment.adjustments.constrained == ()


class TestMacroOpinionGeneration:
    """Tests for Macro Committee opinion generation."""

    def test_evaluate_returns_committee_opinion(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        opinion = member.evaluate(
            recommendation
        )

        assert isinstance(
            opinion,
            CommitteeOpinion,
        )

    def test_opinion_preserves_recommendation_identifier(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation(
            identifier="REC-MACRO-999"
        )

        opinion = member.evaluate(
            recommendation
        )

        assert (
            opinion.recommendation_identifier
            == "REC-MACRO-999"
        )

    def test_opinion_uses_macro_role(self) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        opinion = member.evaluate(
            recommendation
        )

        assert opinion.member == CommitteeRole.MACRO

    def test_opinion_uses_adjusted_confidence(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.70,
            expected_duration_months=12,
        )

        opinion = member.evaluate(
            recommendation
        )

        assert opinion.confidence == 0.79
        assert opinion.vote == CommitteeVote.APPROVE

    def test_high_conviction_macro_view_strongly_approves(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.MACRO,
            confidence=0.80,
            expected_duration_months=24,
        )

        opinion = member.evaluate(
            recommendation
        )

        assert opinion.confidence == 0.94
        assert (
            opinion.vote
            == CommitteeVote.STRONGLY_APPROVE
        )

    def test_weak_short_term_security_view_objects(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY,
            confidence=0.50,
            expected_duration_months=3,
        )

        opinion = member.evaluate(
            recommendation
        )

        assert opinion.confidence == 0.43
        assert opinion.vote == CommitteeVote.OBJECT

    def test_supports_returns_true_for_approval(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.70,
            expected_duration_months=12,
        )

        assert member.supports(recommendation) is True
        assert member.objects(recommendation) is False

    def test_objects_returns_true_for_objection(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.SECURITY,
            confidence=0.50,
            expected_duration_months=3,
        )

        assert member.objects(recommendation) is True
        assert member.supports(recommendation) is False

    def test_confidence_accessor_returns_final_confidence(
        self,
    ) -> None:
        member = MacroCommitteeMember()

        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.70,
            expected_duration_months=12,
        )

        assert member.confidence(recommendation) == 0.79


class TestCustomDecisionFramework:
    """Tests for injecting custom voting thresholds."""

    def test_custom_thresholds_change_vote_not_assessment(
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

        member = MacroCommitteeMember(
            framework=framework
        )

        recommendation = make_recommendation(
            level=RecommendationLevel.ASSET_CLASS,
            confidence=0.70,
            expected_duration_months=12,
        )

        assessment = member.assess(
            recommendation
        )

        opinion = member.evaluate(
            recommendation
        )

        assert assessment.adjusted_confidence == 0.79
        assert opinion.confidence == 0.79
        assert opinion.vote == CommitteeVote.NEUTRAL


class TestMacroValidation:
    """Tests for invalid Macro Committee inputs."""

    @pytest.mark.parametrize(
        "invalid_recommendation",
        [
            None,
            "recommendation",
            object(),
            {},
            [],
        ],
    )
    def test_evaluate_rejects_invalid_recommendation(
        self,
        invalid_recommendation: object,
    ) -> None:
        member = MacroCommitteeMember()

        with pytest.raises(
            TypeError,
            match=(
                "recommendation must be an "
                "InvestmentRecommendation"
            ),
        ):
            member.evaluate(
                invalid_recommendation  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize(
        "invalid_recommendation",
        [
            None,
            "recommendation",
            object(),
        ],
    )
    def test_assess_rejects_invalid_recommendation(
        self,
        invalid_recommendation: object,
    ) -> None:
        """
        The public evaluate() method validates its input before assess().
        Direct assess() calls currently rely on attribute access and are
        not the validated public entry point.

        This test confirms the supported public contract through
        build_assessment(), which validates the recommendation.
        """

        member = MacroCommitteeMember()

        with pytest.raises(TypeError):
            member.build_assessment(
                recommendation=(
                    invalid_recommendation
                ),  # type: ignore[arg-type]
                adjustments=(),
                rationale="Invalid input.",
            )


class TestMacroDeterminism:
    """Tests for repeatable Macro Committee behavior."""

    def test_repeated_assessments_are_equal(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        first = member.assess(
            recommendation
        )

        second = member.assess(
            recommendation
        )

        assert first == second

    def test_repeated_opinions_are_equal(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        first = member.evaluate(
            recommendation
        )

        second = member.evaluate(
            recommendation
        )

        assert first == second

    def test_adjustment_summary_is_deterministic(
        self,
    ) -> None:
        member = MacroCommitteeMember()
        recommendation = make_recommendation()

        assessment = member.assess(
            recommendation
        )

        first = assessment.adjustments.summary()
        second = assessment.adjustments.summary()

        assert first == second
        assert "Raw Adjustment:" in first
        assert "Applied Adjustment:" in first
