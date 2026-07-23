"""Convert economic themes into explainable investment theses."""

from __future__ import annotations

from intelligence.theme import (
    EconomicTheme,
    ThemeCategory,
    ThemeDirection,
    ThemeSet,
)
from intelligence.thesis import (
    InvestmentThesis,
    InvestmentThesisSet,
    ThesisDirection,
    ThesisHorizon,
    ThesisStatus,
)


class InvestmentThesisEngine:
    """
    Generate investment theses from an economic ThemeSet.

    The engine identifies investment implications, beneficiaries, losers,
    catalysts, risks, and invalidation conditions. It does not create trades
    or determine portfolio allocations.
    """

    def generate(
        self,
        theme_set: ThemeSet,
    ) -> InvestmentThesisSet:
        """Generate investment theses from economic themes."""

        if not isinstance(theme_set, ThemeSet):
            raise TypeError(
                "theme_set must be a ThemeSet"
            )

        theses = [
            self._build_thesis(theme)
            for theme in theme_set.themes
        ]

        unique_theses = self._deduplicate(theses)

        confidence = self._calculate_confidence(
            theme_set=theme_set,
            theses=unique_theses,
        )

        summary = self._build_summary(
            theses=unique_theses,
        )

        return InvestmentThesisSet(
            theses=tuple(unique_theses),
            confidence=confidence,
            summary=summary,
        )

    def _build_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        builders = {
            "disinflation-with-positive-growth":
                self._disinflation_growth_thesis,
            "quality-risk-assets-supported":
                self._quality_assets_thesis,
            "defensive-positioning":
                self._defensive_positioning_thesis,
            "credit-quality-differentiation":
                self._credit_quality_thesis,
            "cyclical-growth-leadership":
                self._cyclical_growth_thesis,
            "higher-for-longer-rate-risk":
                self._higher_for_longer_thesis,
            "inflation-resilience":
                self._inflation_resilience_thesis,
            "margin-pressure":
                self._margin_pressure_thesis,
            "manufacturing-weakness":
                self._manufacturing_weakness_thesis,
            "tightening-credit-conditions":
                self._tightening_credit_thesis,
            "resilient-household-demand":
                self._household_demand_thesis,
            "material-recession-tail-risk":
                self._recession_tail_risk_thesis,
            "material-inflation-tail-risk":
                self._inflation_tail_risk_thesis,
        }

        builder = builders.get(theme.identifier)

        if builder is not None:
            return builder(theme)

        return self._generic_thesis(theme)

    def _disinflation_growth_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="long-duration-quality-in-disinflation",
            title="Long-Duration Quality Benefits From Disinflation",
            direction=ThesisDirection.BULLISH,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "If inflation continues to moderate while growth remains "
                "positive, high-quality equities and duration-sensitive "
                "bonds should benefit from stable earnings and reduced "
                "interest-rate pressure."
            ),
            contradicting_evidence=(
                "Inflation-sensitive inputs remain vulnerable to renewed shocks.",
                "Policy rates may remain restrictive despite lower inflation.",
            ),
            beneficiaries=(
                "quality_growth_equities",
                "investment_grade_bonds",
                "intermediate_government_bonds",
            ),
            losers=(
                "cash_equivalents",
                "inflation_sensitive_short_duration_assets",
            ),
            catalysts=(
                "Further moderation in core inflation",
                "Stable or improving corporate earnings",
                "A less restrictive monetary-policy outlook",
            ),
            risks=(
                "Inflation reacceleration",
                "Unexpected earnings deterioration",
                "A renewed rise in long-term interest rates",
            ),
            increase_conditions=(
                "Inflation improves for multiple reporting periods",
                "Credit conditions remain stable",
                "Labor weakness remains limited",
            ),
            reduce_conditions=(
                "Inflation progress stalls",
                "Growth weakens toward contraction",
                "Credit spreads widen materially",
            ),
            invalidation_conditions=(
                "Inflation deteriorates while growth falls",
                "The economy enters a broad recession",
            ),
        )

    def _quality_assets_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="quality-balance-sheet-leadership",
            title="Strong Balance Sheets Lead Risk Assets",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "In a stable-growth environment, profitable companies with "
                "durable cash flows, pricing power, and low refinancing needs "
                "should outperform lower-quality risk assets."
            ),
            contradicting_evidence=(
                "Highly leveraged companies may outperform during aggressive easing.",
            ),
            beneficiaries=(
                "large_cap_quality_equities",
                "profitable_growth_companies",
                "investment_grade_credit",
            ),
            losers=(
                "unprofitable_growth_companies",
                "highly_leveraged_companies",
                "weak_balance_sheet_issuers",
            ),
            catalysts=(
                "Stable earnings revisions",
                "Continued access to affordable financing",
                "Moderate economic growth",
            ),
            risks=(
                "Speculative risk appetite broadens sharply",
                "Quality valuations become excessive",
                "Economic growth contracts",
            ),
            increase_conditions=(
                "Quality earnings remain resilient",
                "Default expectations remain contained",
                "Balance-sheet strength is rewarded by markets",
            ),
            reduce_conditions=(
                "Valuation premiums become extreme",
                "Lower-quality assets begin showing durable fundamental improvement",
            ),
            invalidation_conditions=(
                "Broad earnings collapse affects quality companies equally",
                "A liquidity surge causes persistent low-quality leadership",
            ),
        )

    def _defensive_positioning_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="defensive-assets-during-contraction",
            title="Defensive Assets Outperform During Economic Contraction",
            direction=ThesisDirection.BEARISH,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "If economic contraction deepens, defensive equities, "
                "high-quality government bonds, and cash should outperform "
                "economically sensitive and highly leveraged assets."
            ),
            contradicting_evidence=(
                "Markets may price a recovery before economic data improves.",
                "Fiscal or monetary support could shorten the downturn.",
            ),
            beneficiaries=(
                "government_bonds",
                "defensive_equities",
                "cash",
                "high_quality_credit",
            ),
            losers=(
                "cyclical_equities",
                "high_yield_bonds",
                "small_cap_equities",
            ),
            catalysts=(
                "Weakening employment conditions",
                "Declining corporate earnings",
                "Wider credit spreads",
            ),
            risks=(
                "Rapid policy intervention",
                "A faster-than-expected growth recovery",
                "Inflation limiting bond performance",
            ),
            increase_conditions=(
                "Labor conditions weaken",
                "Consumer activity contracts",
                "Credit availability deteriorates",
            ),
            reduce_conditions=(
                "Leading indicators stabilize",
                "Financial conditions ease materially",
                "Earnings expectations stop falling",
            ),
            invalidation_conditions=(
                "Growth returns to sustained expansion",
                "Recession probability falls below a material threshold",
            ),
        )

    def _credit_quality_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="higher-quality-credit-outperforms",
            title="Higher-Quality Credit Outperforms Lower-Quality Borrowers",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "As growth slows and refinancing becomes more difficult, "
                "higher-quality borrowers should outperform leveraged issuers "
                "with weak cash flows and near-term funding needs."
            ),
            contradicting_evidence=(
                "Credit spreads may already discount significant weakness.",
            ),
            beneficiaries=(
                "investment_grade_bonds",
                "short_duration_high_quality_credit",
                "cash_rich_companies",
            ),
            losers=(
                "high_yield_bonds",
                "leveraged_loans",
                "distressed_borrowers",
            ),
            catalysts=(
                "Higher refinancing costs",
                "Rising default expectations",
                "Tighter bank-lending standards",
            ),
            risks=(
                "Aggressive monetary easing",
                "Stronger-than-expected corporate cash flow",
                "Rapid spread compression",
            ),
            increase_conditions=(
                "Default rates rise",
                "Credit spreads widen",
                "Lending standards tighten further",
            ),
            reduce_conditions=(
                "Refinancing markets reopen",
                "Corporate leverage declines",
                "Default expectations stabilize",
            ),
            invalidation_conditions=(
                "Lower-quality credit fundamentals improve broadly",
                "Credit conditions shift decisively toward easing",
            ),
        )

    def _cyclical_growth_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="cyclical-assets-benefit-from-reacceleration",
            title="Cyclical Assets Benefit From Economic Reacceleration",
            direction=ThesisDirection.BULLISH,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "If economic activity reaccelerates, cyclical equities, "
                "industrial businesses, commodities, and selected credit "
                "assets should benefit from stronger demand."
            ),
            contradicting_evidence=(
                "Higher interest rates may offset stronger nominal growth.",
                "Inflation may reduce real demand.",
            ),
            beneficiaries=(
                "industrial_equities",
                "materials_equities",
                "cyclical_consumer_equities",
                "commodities",
            ),
            losers=(
                "long_duration_government_bonds",
                "rate_sensitive_defensive_assets",
            ),
            catalysts=(
                "Improving manufacturing activity",
                "Stronger consumer demand",
                "Rising business investment",
            ),
            risks=(
                "Inflation reacceleration",
                "Restrictive policy",
                "Demand fails to broaden",
            ),
            increase_conditions=(
                "Manufacturing improves",
                "Earnings revisions turn positive",
                "Credit demand strengthens without rising defaults",
            ),
            reduce_conditions=(
                "Growth momentum stalls",
                "Interest rates rise faster than earnings expectations",
            ),
            invalidation_conditions=(
                "Growth weakens into contraction",
                "Manufacturing deteriorates persistently",
            ),
        )

    def _higher_for_longer_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="rate-sensitive-assets-face-pressure",
            title="Rate-Sensitive Assets Face Higher-for-Longer Pressure",
            direction=ThesisDirection.BEARISH,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "If economic activity remains strong, monetary policy may "
                "stay restrictive and pressure long-duration bonds, highly "
                "valued growth assets, and leveraged real estate."
            ),
            contradicting_evidence=(
                "Inflation could continue falling despite strong growth.",
            ),
            beneficiaries=(
                "short_duration_bonds",
                "floating_rate_assets",
                "cash_generative_value_equities",
            ),
            losers=(
                "long_duration_government_bonds",
                "high_multiple_growth_equities",
                "leveraged_real_estate",
            ),
            catalysts=(
                "Persistent inflation",
                "Stronger economic data",
                "Delayed policy easing",
            ),
            risks=(
                "Rapid disinflation",
                "Unexpected policy easing",
                "Financial instability",
            ),
            increase_conditions=(
                "Policy expectations move toward fewer rate cuts",
                "Long-term yields remain elevated",
                "Nominal growth stays strong",
            ),
            reduce_conditions=(
                "Inflation falls faster than expected",
                "Labor demand weakens materially",
            ),
            invalidation_conditions=(
                "Policy shifts decisively toward easing",
                "Long-term yields decline with stable growth",
            ),
        )

    def _inflation_resilience_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="real-assets-provide-inflation-resilience",
            title="Real Assets Provide Inflation Resilience",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "If inflation remains persistent while growth weakens, "
                "select real assets and inflation-linked securities may "
                "preserve purchasing power better than nominal assets."
            ),
            contradicting_evidence=(
                "Demand destruction could cause commodity prices to fall.",
            ),
            beneficiaries=(
                "inflation_linked_bonds",
                "energy_equities",
                "selected_commodities",
                "infrastructure_assets",
            ),
            losers=(
                "long_duration_nominal_bonds",
                "low_margin_companies",
                "rate_sensitive_growth_assets",
            ),
            catalysts=(
                "Persistent core inflation",
                "Commodity-supply constraints",
                "Rising inflation expectations",
            ),
            risks=(
                "Sharp demand contraction",
                "Commodity-price reversal",
                "Aggressive monetary tightening",
            ),
            increase_conditions=(
                "Inflation expectations rise",
                "Supply constraints persist",
                "Real yields remain unfavorable to nominal assets",
            ),
            reduce_conditions=(
                "Inflation normalizes",
                "Commodity demand weakens materially",
            ),
            invalidation_conditions=(
                "Inflation returns sustainably toward target",
                "Deflationary contraction becomes the dominant scenario",
            ),
        )

    def _margin_pressure_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="pricing-power-determines-equity-winners",
            title="Pricing Power Determines Equity Winners",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "When input costs remain elevated and growth is weak, "
                "companies with pricing power and efficient cost structures "
                "should outperform low-margin businesses."
            ),
            contradicting_evidence=(
                "Input costs may fall faster than final demand.",
            ),
            beneficiaries=(
                "high_margin_equities",
                "companies_with_pricing_power",
                "asset_light_businesses",
            ),
            losers=(
                "low_margin_equities",
                "labor_intensive_businesses",
                "highly_competitive_industries",
            ),
            catalysts=(
                "Persistent wage or input-cost pressure",
                "Weak revenue growth",
                "Negative earnings revisions",
            ),
            risks=(
                "Rapid cost normalization",
                "Stronger nominal demand",
                "Unexpected productivity gains",
            ),
            increase_conditions=(
                "Corporate margins decline broadly",
                "Input costs remain elevated",
                "Pricing power becomes more differentiated",
            ),
            reduce_conditions=(
                "Margins stabilize",
                "Producer costs decline materially",
            ),
            invalidation_conditions=(
                "Profit margins recover broadly",
                "Input costs fall while demand strengthens",
            ),
        )

    def _manufacturing_weakness_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="industrial-cyclicals-face-near-term-headwinds",
            title="Industrial Cyclicals Face Near-Term Headwinds",
            direction=ThesisDirection.BEARISH,
            horizon=ThesisHorizon.TACTICAL,
            proposition=(
                "Deteriorating manufacturing activity may pressure industrial "
                "earnings, commodity demand, and economically sensitive credit."
            ),
            contradicting_evidence=(
                "Inventory normalization could support a quick recovery.",
            ),
            beneficiaries=(
                "defensive_equities",
                "government_bonds",
                "service_oriented_businesses",
            ),
            losers=(
                "industrial_equities",
                "materials_equities",
                "cyclical_credit",
            ),
            catalysts=(
                "Weak new orders",
                "Declining production",
                "Inventory reductions",
            ),
            risks=(
                "Manufacturing rebounds",
                "Fiscal investment supports industrial demand",
            ),
            increase_conditions=(
                "New orders remain weak",
                "Industrial earnings revisions fall",
            ),
            reduce_conditions=(
                "Purchasing-manager data improves",
                "Production stabilizes",
            ),
            invalidation_conditions=(
                "Manufacturing shifts to sustained improvement",
            ),
        )

    def _tightening_credit_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="credit-dependent-assets-underperform",
            title="Credit-Dependent Assets Underperform",
            direction=ThesisDirection.BEARISH,
            horizon=ThesisHorizon.CYCLICAL,
            proposition=(
                "Tighter lending standards and reduced financing availability "
                "should pressure small companies, leveraged borrowers, and "
                "credit-dependent property assets."
            ),
            contradicting_evidence=(
                "Private capital may replace traditional bank lending.",
            ),
            beneficiaries=(
                "cash_rich_companies",
                "high_quality_credit",
                "large_cap_equities",
            ),
            losers=(
                "small_cap_equities",
                "leveraged_real_estate",
                "lower_quality_credit",
            ),
            catalysts=(
                "Tighter lending standards",
                "Higher borrowing costs",
                "Slower credit creation",
            ),
            risks=(
                "Policy support improves liquidity",
                "Capital markets reopen",
            ),
            increase_conditions=(
                "Loan growth contracts",
                "Delinquencies rise",
                "Bank standards tighten",
            ),
            reduce_conditions=(
                "Credit availability improves",
                "Borrowing costs decline",
            ),
            invalidation_conditions=(
                "Credit conditions shift to sustained easing",
            ),
        )

    def _household_demand_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="consumer-demand-supports-selected-equities",
            title="Resilient Consumers Support Selected Equities",
            direction=ThesisDirection.BULLISH,
            horizon=ThesisHorizon.TACTICAL,
            proposition=(
                "Strong labor and household conditions should support selected "
                "consumer businesses, particularly those serving financially "
                "healthy customers."
            ),
            contradicting_evidence=(
                "Consumer strength may be uneven across income groups.",
            ),
            beneficiaries=(
                "consumer_services_equities",
                "travel_and_leisure_equities",
                "high_quality_consumer_discretionary",
            ),
            losers=(
                "highly_indebted_consumers",
                "subprime_consumer_lenders",
            ),
            catalysts=(
                "Stable employment",
                "Positive real-income growth",
                "Healthy consumer spending",
            ),
            risks=(
                "Rising delinquencies",
                "Falling household savings",
                "Labor-market weakness",
            ),
            increase_conditions=(
                "Real wages improve",
                "Consumer confidence strengthens",
            ),
            reduce_conditions=(
                "Delinquencies rise",
                "Retail activity weakens",
            ),
            invalidation_conditions=(
                "Labor conditions weaken materially",
                "Consumer spending contracts broadly",
            ),
        )

    def _recession_tail_risk_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="maintain-downside-hedges",
            title="Maintain Downside Protection Against Recession Risk",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.TACTICAL,
            proposition=(
                "Even when recession is not the base case, material downside "
                "probability supports maintaining liquidity, quality exposure, "
                "and selective portfolio hedges."
            ),
            contradicting_evidence=(
                "Growth may remain resilient and make hedges costly.",
            ),
            beneficiaries=(
                "government_bonds",
                "cash",
                "defensive_equities",
                "downside_hedges",
            ),
            losers=(
                "high_beta_equities",
                "lower_quality_credit",
            ),
            catalysts=(
                "Weak leading indicators",
                "Rising unemployment",
                "Wider credit spreads",
            ),
            risks=(
                "Economic resilience",
                "Rapid risk-asset recovery",
                "Hedging costs",
            ),
            increase_conditions=(
                "Recession probability rises",
                "Labor conditions weaken",
            ),
            reduce_conditions=(
                "Leading indicators improve",
                "Credit conditions stabilize",
            ),
            invalidation_conditions=(
                "Recession probability becomes immaterial",
                "Growth reaccelerates broadly",
            ),
        )

    def _inflation_tail_risk_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        return self._create_thesis(
            theme=theme,
            identifier="retain-inflation-protection",
            title="Retain Select Inflation Protection",
            direction=ThesisDirection.SELECTIVE,
            horizon=ThesisHorizon.TACTICAL,
            proposition=(
                "A material inflation tail risk supports retaining measured "
                "exposure to inflation-linked securities and real assets."
            ),
            contradicting_evidence=(
                "Inflation may continue normalizing without renewed pressure.",
            ),
            beneficiaries=(
                "inflation_linked_bonds",
                "selected_commodities",
                "energy_equities",
            ),
            losers=(
                "long_duration_nominal_bonds",
                "low_pricing_power_companies",
            ),
            catalysts=(
                "Rising inflation expectations",
                "Supply disruptions",
                "Persistent services inflation",
            ),
            risks=(
                "Demand contraction",
                "Commodity-price declines",
                "Faster disinflation",
            ),
            increase_conditions=(
                "Inflation probability rises",
                "Market inflation expectations increase",
            ),
            reduce_conditions=(
                "Inflation measures normalize",
                "Supply constraints ease",
            ),
            invalidation_conditions=(
                "Inflation risk becomes immaterial",
                "Deflation becomes the dominant risk",
            ),
        )

    def _generic_thesis(
        self,
        theme: EconomicTheme,
    ) -> InvestmentThesis:
        direction = self._map_direction(
            theme.direction
        )

        return self._create_thesis(
            theme=theme,
            identifier=(
                f"{theme.identifier}-investment-implication"
            ),
            title=f"Investment Implications of {theme.title}",
            direction=direction,
            horizon=self._infer_horizon(theme),
            proposition=(
                f"If the '{theme.title}' theme persists, the affected "
                "asset classes may experience differentiated performance "
                "consistent with the theme's economic direction."
            ),
            contradicting_evidence=(
                "The theme may already be reflected in market prices.",
            ),
            beneficiaries=theme.affected_asset_classes,
            losers=(),
            catalysts=theme.supporting_evidence,
            risks=theme.risks or (
                "The economic theme may weaken.",
            ),
            increase_conditions=(
                f"Evidence supporting '{theme.title}' strengthens.",
            ),
            reduce_conditions=(
                f"Evidence supporting '{theme.title}' weakens.",
            ),
            invalidation_conditions=(
                f"The '{theme.title}' theme reverses materially.",
            ),
        )

    def _create_thesis(
        self,
        *,
        theme: EconomicTheme,
        identifier: str,
        title: str,
        direction: ThesisDirection,
        horizon: ThesisHorizon,
        proposition: str,
        contradicting_evidence: tuple[str, ...],
        beneficiaries: tuple[str, ...],
        losers: tuple[str, ...],
        catalysts: tuple[str, ...],
        risks: tuple[str, ...],
        increase_conditions: tuple[str, ...],
        reduce_conditions: tuple[str, ...],
        invalidation_conditions: tuple[str, ...],
    ) -> InvestmentThesis:
        return InvestmentThesis(
            identifier=identifier,
            title=title,
            source_theme_identifier=theme.identifier,
            source_theme_category=theme.category,
            direction=direction,
            horizon=horizon,
            status=ThesisStatus.ACTIVE,
            confidence=self._thesis_confidence(theme),
            proposition=proposition,
            supporting_evidence=theme.supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            beneficiaries=beneficiaries,
            losers=losers,
            catalysts=catalysts,
            risks=risks,
            increase_conviction_conditions=increase_conditions,
            reduce_conviction_conditions=reduce_conditions,
            invalidation_conditions=invalidation_conditions,
            expected_duration_months=theme.expected_duration_months,
        )

    def _thesis_confidence(
        self,
        theme: EconomicTheme,
    ) -> float:
        direction_adjustment = {
            ThemeDirection.POSITIVE: 0.02,
            ThemeDirection.NEGATIVE: 0.02,
            ThemeDirection.MIXED: -0.05,
            ThemeDirection.NEUTRAL: -0.10,
        }[theme.direction]

        value = theme.confidence + direction_adjustment

        return self._clamp(value)

    def _infer_horizon(
        self,
        theme: EconomicTheme,
    ) -> ThesisHorizon:
        if theme.category == ThemeCategory.STRUCTURAL:
            return ThesisHorizon.STRUCTURAL

        if theme.expected_duration_months <= 6:
            return ThesisHorizon.TACTICAL

        return ThesisHorizon.CYCLICAL

    def _map_direction(
        self,
        direction: ThemeDirection,
    ) -> ThesisDirection:
        mapping = {
            ThemeDirection.POSITIVE: ThesisDirection.BULLISH,
            ThemeDirection.NEGATIVE: ThesisDirection.BEARISH,
            ThemeDirection.MIXED: ThesisDirection.SELECTIVE,
            ThemeDirection.NEUTRAL: ThesisDirection.NEUTRAL,
        }

        return mapping[direction]

    def _calculate_confidence(
        self,
        *,
        theme_set: ThemeSet,
        theses: list[InvestmentThesis],
    ) -> float:
        average_thesis_confidence = sum(
            thesis.confidence
            for thesis in theses
        ) / len(theses)

        value = (
            theme_set.confidence * 0.55
            + average_thesis_confidence * 0.45
        )

        return self._clamp(value)

    def _build_summary(
        self,
        *,
        theses: list[InvestmentThesis],
    ) -> str:
        leading_thesis = max(
            theses,
            key=lambda thesis: thesis.confidence,
        )

        bullish_count = sum(
            thesis.direction == ThesisDirection.BULLISH
            for thesis in theses
        )

        bearish_count = sum(
            thesis.direction == ThesisDirection.BEARISH
            for thesis in theses
        )

        selective_count = sum(
            thesis.direction == ThesisDirection.SELECTIVE
            for thesis in theses
        )

        return (
            f"{len(theses)} investment theses were generated: "
            f"{bullish_count} bullish, "
            f"{bearish_count} bearish, and "
            f"{selective_count} selective. "
            f"The highest-conviction thesis is "
            f"'{leading_thesis.title}'."
        )

    def _deduplicate(
        self,
        theses: list[InvestmentThesis],
    ) -> list[InvestmentThesis]:
        unique: dict[str, InvestmentThesis] = {}

        for thesis in theses:
            existing = unique.get(thesis.identifier)

            if (
                existing is None
                or thesis.confidence > existing.confidence
            ):
                unique[thesis.identifier] = thesis

        return list(unique.values())

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return round(
            max(0.0, min(1.0, value)),
            4,
        )
