"""Transparent rules that convert investment theses into recommendations."""

from __future__ import annotations

from collections.abc import Callable

from intelligence.recommendation import (
    ExpectedReturn,
    ExpectedRisk,
    InvestmentRecommendation,
    RecommendationAction,
    RecommendationLevel,
    RecommendationMagnitude,
)
from intelligence.recommendation_builder import RecommendationBuilder
from intelligence.thesis import (
    InvestmentThesis,
    ThesisDirection,
    ThesisHorizon,
    ThesisStatus,
)

RecommendationRule = Callable[
    [InvestmentThesis],
    tuple[InvestmentRecommendation, ...],
]


class RecommendationRules:
    """
    Apply transparent investment rules to an InvestmentThesis.

    Each known thesis can produce one or more standardized recommendations.
    Unknown theses fall back to a generic recommendation so the pipeline
    remains extensible.
    """

    def __init__(
        self,
        builder: RecommendationBuilder | None = None,
    ) -> None:
        self._builder = builder or RecommendationBuilder()

        self._rules: dict[str, RecommendationRule] = {
            "long-duration-quality-in-disinflation":
                self._disinflation_quality_rules,
            "quality-balance-sheet-leadership":
                self._quality_balance_sheet_rules,
            "defensive-assets-during-contraction":
                self._defensive_contraction_rules,
            "higher-quality-credit-outperforms":
                self._credit_quality_rules,
            "cyclical-assets-benefit-from-reacceleration":
                self._cyclical_reacceleration_rules,
            "rate-sensitive-assets-face-pressure":
                self._higher_for_longer_rules,
            "real-assets-provide-inflation-resilience":
                self._inflation_resilience_rules,
            "pricing-power-determines-equity-winners":
                self._pricing_power_rules,
            "industrial-cyclicals-face-near-term-headwinds":
                self._manufacturing_weakness_rules,
            "credit-dependent-assets-underperform":
                self._tight_credit_rules,
            "consumer-demand-supports-selected-equities":
                self._consumer_resilience_rules,
            "maintain-downside-hedges":
                self._recession_hedge_rules,
            "retain-inflation-protection":
                self._inflation_hedge_rules,
        }

    def apply(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        """Return recommendations generated from one thesis."""

        if not isinstance(thesis, InvestmentThesis):
            raise TypeError(
                "thesis must be an InvestmentThesis"
            )

        if thesis.status == ThesisStatus.INVALIDATED:
            return ()

        rule = self._rules.get(thesis.identifier)

        if rule is None:
            return self._generic_rule(thesis)

        return rule(thesis)

    def _disinflation_quality_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier=(
                    "overweight-investment-grade-bonds-"
                    "during-disinflation"
                ),
                title=(
                    "Overweight Investment-Grade Bonds "
                    "During Disinflation"
                ),
                level=RecommendationLevel.ASSET_CLASS,
                target="investment_grade_bonds",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Moderating inflation and positive growth should "
                    "support high-quality bonds while limiting default risk."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.LOW,
            ),
            self._build(
                thesis=thesis,
                identifier=(
                    "accumulate-quality-growth-equities-"
                    "during-disinflation"
                ),
                title=(
                    "Accumulate Quality Growth Equities "
                    "During Disinflation"
                ),
                level=RecommendationLevel.ASSET_CLASS,
                target="quality_growth_equities",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.03,
                rationale=(
                    "Falling inflation pressure may support valuation "
                    "multiples while stable growth protects earnings."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.MODERATE,
            ),
        )

    def _quality_balance_sheet_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="overweight-large-cap-quality-equities",
                title="Overweight Large-Cap Quality Equities",
                level=RecommendationLevel.ASSET_CLASS,
                target="large_cap_quality_equities",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Profitable companies with durable cash flows and "
                    "limited refinancing needs should lead lower-quality "
                    "risk assets."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.MODERATE,
            ),
            self._build(
                thesis=thesis,
                identifier="underweight-weak-balance-sheet-issuers",
                title="Underweight Weak Balance-Sheet Issuers",
                level=RecommendationLevel.ASSET_CLASS,
                target="weak_balance_sheet_issuers",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.02,
                rationale=(
                    "Companies with weak cash flow and substantial "
                    "refinancing needs remain vulnerable to tighter capital."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _defensive_contraction_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="overweight-government-bonds-in-contraction",
                title="Overweight Government Bonds During Contraction",
                level=RecommendationLevel.ASSET_CLASS,
                target="government_bonds",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.LARGE,
                confidence_adjustment=0.00,
                rationale=(
                    "Weakening growth should support high-quality duration "
                    "and increase demand for defensive assets."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.LOW,
            ),
            self._build(
                thesis=thesis,
                identifier="underweight-cyclical-equities-in-contraction",
                title="Underweight Cyclical Equities During Contraction",
                level=RecommendationLevel.ASSET_CLASS,
                target="cyclical_equities",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.LARGE,
                confidence_adjustment=-0.01,
                rationale=(
                    "Cyclical earnings and valuations are vulnerable to "
                    "falling demand and weaker economic activity."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _credit_quality_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="overweight-investment-grade-credit",
                title="Overweight Investment-Grade Credit",
                level=RecommendationLevel.ASSET_CLASS,
                target="investment_grade_credit",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Higher-quality borrowers should be more resilient "
                    "to slower growth and restrictive refinancing conditions."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.LOW,
            ),
            self._build(
                thesis=thesis,
                identifier="underweight-lower-quality-credit",
                title="Underweight Lower-Quality Credit",
                level=RecommendationLevel.ASSET_CLASS,
                target="lower_quality_credit",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.02,
                rationale=(
                    "Leveraged issuers face greater refinancing, default, "
                    "and spread-widening risks."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _cyclical_reacceleration_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="overweight-cyclical-equities",
                title="Overweight Cyclical Equities",
                level=RecommendationLevel.ASSET_CLASS,
                target="cyclical_equities",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Improving economic activity should support earnings "
                    "for economically sensitive companies."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.HIGH,
            ),
            self._build(
                thesis=thesis,
                identifier="accumulate-industrials",
                title="Accumulate Industrial Equities",
                level=RecommendationLevel.SECTOR,
                target="industrials",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.03,
                rationale=(
                    "Improving production, orders, and capital spending "
                    "should support industrial businesses."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.MODERATE,
            ),
        )

    def _higher_for_longer_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="underweight-long-duration-government-bonds",
                title="Underweight Long-Duration Government Bonds",
                level=RecommendationLevel.ASSET_CLASS,
                target="long_duration_government_bonds",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Persistent economic strength may keep yields elevated "
                    "and pressure long-duration bond prices."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
            self._build(
                thesis=thesis,
                identifier="overweight-short-duration-bonds",
                title="Overweight Short-Duration Bonds",
                level=RecommendationLevel.ASSET_CLASS,
                target="short_duration_bonds",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.02,
                rationale=(
                    "Short-duration bonds should be less sensitive to "
                    "persistent interest-rate pressure."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.LOW,
            ),
        )

    def _inflation_resilience_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="accumulate-inflation-linked-bonds",
                title="Accumulate Inflation-Linked Bonds",
                level=RecommendationLevel.ASSET_CLASS,
                target="inflation_linked_bonds",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Inflation-linked bonds may preserve purchasing power "
                    "if inflation remains persistent."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.MODERATE,
            ),
            self._build(
                thesis=thesis,
                identifier="accumulate-selected-real-assets",
                title="Accumulate Selected Real Assets",
                level=RecommendationLevel.ASSET_CLASS,
                target="selected_real_assets",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=-0.05,
                rationale=(
                    "Selected real assets may benefit from persistent "
                    "inflation and constrained supply."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _pricing_power_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="overweight-companies-with-pricing-power",
                title="Overweight Companies With Pricing Power",
                level=RecommendationLevel.ASSET_CLASS,
                target="companies_with_pricing_power",
                action=RecommendationAction.OVERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Businesses able to pass through input costs should "
                    "protect margins better than low-margin competitors."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.MODERATE,
            ),
            self._build(
                thesis=thesis,
                identifier="avoid-low-margin-businesses",
                title="Avoid Low-Margin Businesses",
                level=RecommendationLevel.ASSET_CLASS,
                target="low_margin_businesses",
                action=RecommendationAction.AVOID,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.02,
                rationale=(
                    "Weak demand and persistent costs may create material "
                    "earnings pressure for low-margin businesses."
                ),
                expected_return=ExpectedReturn.VERY_LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _manufacturing_weakness_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="underweight-industrials-during-manufacturing-weakness",
                title="Underweight Industrials During Manufacturing Weakness",
                level=RecommendationLevel.SECTOR,
                target="industrials",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=0.00,
                rationale=(
                    "Weak orders and production may pressure industrial "
                    "earnings over the tactical horizon."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
        )

    def _tight_credit_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="underweight-small-cap-equities",
                title="Underweight Small-Cap Equities",
                level=RecommendationLevel.ASSET_CLASS,
                target="small_cap_equities",
                action=RecommendationAction.UNDERWEIGHT,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=0.00,
                rationale=(
                    "Small companies are often more dependent on external "
                    "financing and may be vulnerable to tighter credit."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.HIGH,
            ),
            self._build(
                thesis=thesis,
                identifier="avoid-leveraged-real-estate",
                title="Avoid Leveraged Real Estate",
                level=RecommendationLevel.ASSET_CLASS,
                target="leveraged_real_estate",
                action=RecommendationAction.AVOID,
                magnitude=RecommendationMagnitude.MODERATE,
                confidence_adjustment=-0.03,
                rationale=(
                    "High borrowing costs and limited refinancing access "
                    "may pressure leveraged property assets."
                ),
                expected_return=ExpectedReturn.VERY_LOW,
                expected_risk=ExpectedRisk.VERY_HIGH,
            ),
        )

    def _consumer_resilience_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="accumulate-high-quality-consumer-discretionary",
                title="Accumulate High-Quality Consumer Discretionary",
                level=RecommendationLevel.SECTOR,
                target="high_quality_consumer_discretionary",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=0.00,
                rationale=(
                    "Stable employment and real-income growth may support "
                    "consumer demand, particularly among stronger households."
                ),
                expected_return=ExpectedReturn.HIGH,
                expected_risk=ExpectedRisk.MODERATE,
            ),
        )

    def _recession_hedge_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="accumulate-recession-protection",
                title="Accumulate Recession Protection",
                level=RecommendationLevel.MACRO,
                target="recession_protection",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=-0.03,
                rationale=(
                    "Material recession risk supports measured exposure "
                    "to liquidity, duration, and downside protection."
                ),
                expected_return=ExpectedReturn.LOW,
                expected_risk=ExpectedRisk.LOW,
            ),
        )

    def _inflation_hedge_rules(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        return (
            self._build(
                thesis=thesis,
                identifier="retain-measured-inflation-protection",
                title="Retain Measured Inflation Protection",
                level=RecommendationLevel.MACRO,
                target="inflation_protection",
                action=RecommendationAction.ACCUMULATE,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=-0.03,
                rationale=(
                    "A material inflation tail risk supports retaining "
                    "limited exposure to inflation-sensitive assets."
                ),
                expected_return=ExpectedReturn.MODERATE,
                expected_risk=ExpectedRisk.MODERATE,
            ),
        )

    def _generic_rule(
        self,
        thesis: InvestmentThesis,
    ) -> tuple[InvestmentRecommendation, ...]:
        action = self._action_for_direction(
            thesis.direction
        )

        target = (
            thesis.beneficiaries[0]
            if thesis.beneficiaries
            else thesis.source_theme_identifier
        )

        return (
            self._build(
                thesis=thesis,
                identifier=(
                    f"{thesis.identifier}-generic-recommendation"
                ),
                title=f"Review Exposure to {self._display_name(target)}",
                level=RecommendationLevel.ASSET_CLASS,
                target=target,
                action=action,
                magnitude=RecommendationMagnitude.SMALL,
                confidence_adjustment=-0.10,
                rationale=thesis.proposition,
                expected_return=self._return_for_action(action),
                expected_risk=ExpectedRisk.MODERATE,
            ),
        )

    def _build(
        self,
        *,
        thesis: InvestmentThesis,
        identifier: str,
        title: str,
        level: RecommendationLevel,
        target: str,
        action: RecommendationAction,
        magnitude: RecommendationMagnitude,
        confidence_adjustment: float,
        rationale: str,
        expected_return: ExpectedReturn,
        expected_risk: ExpectedRisk,
    ) -> InvestmentRecommendation:
        return self._builder.build(
            identifier=identifier,
            title=title,
            level=level,
            target=target,
            action=action,
            magnitude=magnitude,
            confidence=(
                thesis.confidence
                + confidence_adjustment
            ),
            source_thesis_identifier=thesis.identifier,
            rationale=rationale,
            supporting_evidence=thesis.supporting_evidence,
            contradicting_evidence=(
                thesis.contradicting_evidence
            ),
            catalysts=thesis.catalysts,
            risks=thesis.risks,
            invalidation_conditions=(
                thesis.invalidation_conditions
            ),
            expected_return=expected_return,
            expected_risk=expected_risk,
            expected_duration_months=(
                thesis.expected_duration_months
            ),
        )

    @staticmethod
    def _action_for_direction(
        direction: ThesisDirection,
    ) -> RecommendationAction:
        mapping = {
            ThesisDirection.BULLISH:
                RecommendationAction.OVERWEIGHT,
            ThesisDirection.BEARISH:
                RecommendationAction.UNDERWEIGHT,
            ThesisDirection.SELECTIVE:
                RecommendationAction.ACCUMULATE,
            ThesisDirection.NEUTRAL:
                RecommendationAction.NEUTRAL,
        }

        return mapping[direction]

    @staticmethod
    def _return_for_action(
        action: RecommendationAction,
    ) -> ExpectedReturn:
        mapping = {
            RecommendationAction.OVERWEIGHT:
                ExpectedReturn.HIGH,
            RecommendationAction.ACCUMULATE:
                ExpectedReturn.HIGH,
            RecommendationAction.NEUTRAL:
                ExpectedReturn.MODERATE,
            RecommendationAction.UNDERWEIGHT:
                ExpectedReturn.LOW,
            RecommendationAction.REDUCE:
                ExpectedReturn.LOW,
            RecommendationAction.AVOID:
                ExpectedReturn.VERY_LOW,
        }

        return mapping[action]

    @staticmethod
    def _display_name(
        value: str,
    ) -> str:
        return value.replace("_", " ").title()
