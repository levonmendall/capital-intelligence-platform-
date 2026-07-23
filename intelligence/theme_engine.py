"""Translate economic forecasts into explainable economic themes."""

from __future__ import annotations

from intelligence.forecast import (
    EconomicForecast,
    EconomicScenario,
)
from intelligence.state import (
    Direction,
    Strength,
)
from intelligence.theme import (
    EconomicTheme,
    ThemeCategory,
    ThemeDirection,
    ThemeSet,
)


class ThemeEngine:
    """
    Generate economic themes from an EconomicForecast.

    This engine interprets the forecast but does not make trades,
    assign portfolio weights, or issue CIO guidance.
    """

    def generate(
        self,
        forecast: EconomicForecast,
    ) -> ThemeSet:
        """Generate a collection of themes from a forecast."""

        if not isinstance(forecast, EconomicForecast):
            raise TypeError(
                "forecast must be an EconomicForecast"
            )

        themes: list[EconomicTheme] = []

        themes.extend(
            self._themes_for_base_case(forecast)
        )

        themes.extend(
            self._themes_from_current_state(forecast)
        )

        themes.extend(
            self._themes_from_material_risks(forecast)
        )

        unique_themes = self._deduplicate(themes)

        confidence = self._calculate_confidence(
            forecast=forecast,
            themes=unique_themes,
        )

        summary = self._build_summary(
            forecast=forecast,
            themes=unique_themes,
        )

        return ThemeSet(
            themes=tuple(unique_themes),
            confidence=confidence,
            summary=summary,
        )

    def _themes_for_base_case(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        base_case = forecast.base_case.scenario

        if base_case == EconomicScenario.SOFT_LANDING:
            return self._soft_landing_themes(forecast)

        if base_case == EconomicScenario.RECESSION:
            return self._recession_themes(forecast)

        if base_case == EconomicScenario.REACCELERATION:
            return self._reacceleration_themes(forecast)

        if base_case == EconomicScenario.STAGFLATION:
            return self._stagflation_themes(forecast)

        raise ValueError(
            f"unsupported economic scenario: {base_case}"
        )

    def _soft_landing_themes(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        probability = forecast.probability_for(
            EconomicScenario.SOFT_LANDING
        )

        return [
            EconomicTheme(
                identifier="disinflation-with-positive-growth",
                title="Disinflation With Positive Growth",
                category=ThemeCategory.INFLATION,
                direction=ThemeDirection.POSITIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability,
                ),
                description=(
                    "Inflation is expected to moderate while economic "
                    "growth remains positive."
                ),
                supporting_evidence=(
                    (
                        "Soft landing is the highest-probability "
                        "forecast scenario."
                    ),
                    (
                        f"Soft-landing probability is "
                        f"{probability:.0%}."
                    ),
                    (
                        f"Current growth is assessed as "
                        f"{forecast.current_state.growth.value}."
                    ),
                ),
                risks=(
                    "Inflation could reaccelerate.",
                    "Restrictive policy could weaken demand.",
                ),
                affected_asset_classes=(
                    "equities",
                    "investment_grade_bonds",
                    "government_bonds",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
            EconomicTheme(
                identifier="quality-risk-assets-supported",
                title="Quality Risk Assets Supported",
                category=ThemeCategory.GROWTH,
                direction=ThemeDirection.POSITIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability * 0.95,
                ),
                description=(
                    "Stable growth and improving inflation may support "
                    "profitable companies with strong balance sheets."
                ),
                supporting_evidence=(
                    "The forecast favors continued positive growth.",
                    (
                        f"Labor-market strength is "
                        f"{forecast.current_state.labor_market.value}."
                    ),
                ),
                risks=(
                    "Earnings growth may disappoint.",
                    "Credit conditions may deteriorate.",
                ),
                affected_asset_classes=(
                    "equities",
                    "corporate_bonds",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
        ]

    def _recession_themes(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        probability = forecast.probability_for(
            EconomicScenario.RECESSION
        )

        return [
            EconomicTheme(
                identifier="defensive-positioning",
                title="Defensive Positioning",
                category=ThemeCategory.DEFENSIVE,
                direction=ThemeDirection.POSITIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability,
                ),
                description=(
                    "Weakening economic activity may favor defensive "
                    "assets and businesses with durable cash flows."
                ),
                supporting_evidence=(
                    "Recession is the highest-probability scenario.",
                    (
                        f"Recession probability is "
                        f"{probability:.0%}."
                    ),
                    (
                        f"Current growth is assessed as "
                        f"{forecast.current_state.growth.value}."
                    ),
                ),
                risks=(
                    "Policy support could improve growth.",
                    "Markets may price recovery before data improves.",
                ),
                affected_asset_classes=(
                    "government_bonds",
                    "defensive_equities",
                    "cash",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
            EconomicTheme(
                identifier="credit-quality-differentiation",
                title="Credit Quality Differentiation",
                category=ThemeCategory.CREDIT,
                direction=ThemeDirection.NEGATIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability * 0.95,
                ),
                description=(
                    "Economic weakness may widen the performance gap "
                    "between stronger and weaker borrowers."
                ),
                supporting_evidence=(
                    "The forecast indicates elevated recession risk.",
                    (
                        f"Credit conditions are currently "
                        f"{forecast.current_state.credit.value}."
                    ),
                ),
                risks=(
                    "Credit spreads may already reflect weakness.",
                    "Rapid easing could reduce default risk.",
                ),
                affected_asset_classes=(
                    "high_yield_bonds",
                    "leveraged_loans",
                    "investment_grade_bonds",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
        ]

    def _reacceleration_themes(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        probability = forecast.probability_for(
            EconomicScenario.REACCELERATION
        )

        return [
            EconomicTheme(
                identifier="cyclical-growth-leadership",
                title="Cyclical Growth Leadership",
                category=ThemeCategory.GROWTH,
                direction=ThemeDirection.POSITIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability,
                ),
                description=(
                    "Accelerating economic activity may favor cyclical "
                    "industries and economically sensitive assets."
                ),
                supporting_evidence=(
                    (
                        "Reacceleration is the highest-probability "
                        "scenario."
                    ),
                    (
                        f"Reacceleration probability is "
                        f"{probability:.0%}."
                    ),
                    (
                        f"Consumer strength is "
                        f"{forecast.current_state.consumer.value}."
                    ),
                ),
                risks=(
                    "Inflation may rise with stronger demand.",
                    "Interest rates may remain elevated.",
                ),
                affected_asset_classes=(
                    "cyclical_equities",
                    "commodities",
                    "high_yield_bonds",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
            EconomicTheme(
                identifier="higher-for-longer-rate-risk",
                title="Higher-for-Longer Rate Risk",
                category=ThemeCategory.MONETARY_POLICY,
                direction=ThemeDirection.NEGATIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability * 0.85,
                ),
                description=(
                    "Stronger economic activity may delay monetary "
                    "policy easing and keep longer-term rates elevated."
                ),
                supporting_evidence=(
                    "The forecast favors renewed economic acceleration.",
                    (
                        f"Inflation is currently "
                        f"{forecast.current_state.inflation.value}."
                    ),
                ),
                risks=(
                    "Inflation could continue falling.",
                    "Policy makers may prioritize financial stability.",
                ),
                affected_asset_classes=(
                    "government_bonds",
                    "growth_equities",
                    "real_estate",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
        ]

    def _stagflation_themes(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        probability = forecast.probability_for(
            EconomicScenario.STAGFLATION
        )

        return [
            EconomicTheme(
                identifier="inflation-resilience",
                title="Inflation Resilience",
                category=ThemeCategory.INFLATION,
                direction=ThemeDirection.MIXED,
                confidence=self._weighted_confidence(
                    forecast,
                    probability,
                ),
                description=(
                    "Persistent inflation combined with weak growth may "
                    "favor assets with inflation-sensitive revenues."
                ),
                supporting_evidence=(
                    (
                        "Stagflation is the highest-probability "
                        "scenario."
                    ),
                    (
                        f"Stagflation probability is "
                        f"{probability:.0%}."
                    ),
                    (
                        f"Inflation is assessed as "
                        f"{forecast.current_state.inflation.value}."
                    ),
                ),
                risks=(
                    "Demand destruction could reduce inflation.",
                    "Commodity prices may reverse sharply.",
                ),
                affected_asset_classes=(
                    "commodities",
                    "inflation_linked_bonds",
                    "energy_equities",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
            EconomicTheme(
                identifier="margin-pressure",
                title="Corporate Margin Pressure",
                category=ThemeCategory.GROWTH,
                direction=ThemeDirection.NEGATIVE,
                confidence=self._weighted_confidence(
                    forecast,
                    probability * 0.95,
                ),
                description=(
                    "Weak growth and persistent input costs may pressure "
                    "corporate profit margins."
                ),
                supporting_evidence=(
                    "The forecast combines inflation risk with weakness.",
                    (
                        f"Manufacturing is currently "
                        f"{forecast.current_state.manufacturing.value}."
                    ),
                ),
                risks=(
                    "Companies may retain pricing power.",
                    "Input costs may fall faster than expected.",
                ),
                affected_asset_classes=(
                    "equities",
                    "corporate_bonds",
                ),
                expected_duration_months=forecast.horizon_months,
            ),
        ]

    def _themes_from_current_state(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        state = forecast.current_state
        themes: list[EconomicTheme] = []

        if state.manufacturing == Direction.DETERIORATING:
            themes.append(
                EconomicTheme(
                    identifier="manufacturing-weakness",
                    title="Manufacturing Weakness",
                    category=ThemeCategory.MANUFACTURING,
                    direction=ThemeDirection.NEGATIVE,
                    confidence=self._state_confidence(
                        forecast,
                        adjustment=0.90,
                    ),
                    description=(
                        "Deteriorating manufacturing conditions may "
                        "weigh on industrial activity and cyclical demand."
                    ),
                    supporting_evidence=(
                        "Manufacturing is assessed as deteriorating.",
                    ),
                    risks=(
                        "New orders may recover.",
                        "Inventory normalization may support production.",
                    ),
                    affected_asset_classes=(
                        "industrial_equities",
                        "commodities",
                        "high_yield_bonds",
                    ),
                    expected_duration_months=min(
                        6,
                        forecast.horizon_months,
                    ),
                )
            )

        if state.credit == Direction.DETERIORATING:
            themes.append(
                EconomicTheme(
                    identifier="tightening-credit-conditions",
                    title="Tightening Credit Conditions",
                    category=ThemeCategory.CREDIT,
                    direction=ThemeDirection.NEGATIVE,
                    confidence=self._state_confidence(
                        forecast,
                        adjustment=0.95,
                    ),
                    description=(
                        "Deteriorating credit conditions may constrain "
                        "borrowing, investment, and economic activity."
                    ),
                    supporting_evidence=(
                        "Credit conditions are assessed as deteriorating.",
                    ),
                    risks=(
                        "Policy easing could restore liquidity.",
                        "Bank lending conditions may stabilize.",
                    ),
                    affected_asset_classes=(
                        "corporate_bonds",
                        "financial_equities",
                        "small_cap_equities",
                    ),
                    expected_duration_months=min(
                        9,
                        forecast.horizon_months,
                    ),
                )
            )

        if (
            state.consumer == Strength.STRONG
            and state.labor_market == Strength.STRONG
        ):
            themes.append(
                EconomicTheme(
                    identifier="resilient-household-demand",
                    title="Resilient Household Demand",
                    category=ThemeCategory.CONSUMER,
                    direction=ThemeDirection.POSITIVE,
                    confidence=self._state_confidence(
                        forecast,
                        adjustment=0.90,
                    ),
                    description=(
                        "Strong labor and consumer conditions may sustain "
                        "household demand."
                    ),
                    supporting_evidence=(
                        "Consumer conditions are assessed as strong.",
                        "Labor-market conditions are assessed as strong.",
                    ),
                    risks=(
                        "Household savings may weaken.",
                        "Higher borrowing costs may slow spending.",
                    ),
                    affected_asset_classes=(
                        "consumer_equities",
                        "equities",
                        "corporate_bonds",
                    ),
                    expected_duration_months=min(
                        6,
                        forecast.horizon_months,
                    ),
                )
            )

        return themes

    def _themes_from_material_risks(
        self,
        forecast: EconomicForecast,
    ) -> list[EconomicTheme]:
        themes: list[EconomicTheme] = []

        recession_probability = forecast.probability_for(
            EconomicScenario.RECESSION
        )

        stagflation_probability = forecast.probability_for(
            EconomicScenario.STAGFLATION
        )

        if (
            recession_probability >= 0.25
            and forecast.base_case.scenario
            != EconomicScenario.RECESSION
        ):
            themes.append(
                EconomicTheme(
                    identifier="material-recession-tail-risk",
                    title="Material Recession Tail Risk",
                    category=ThemeCategory.DEFENSIVE,
                    direction=ThemeDirection.NEGATIVE,
                    confidence=self._weighted_confidence(
                        forecast,
                        recession_probability,
                    ),
                    description=(
                        "Recession is not the base case but remains "
                        "probable enough to influence risk management."
                    ),
                    supporting_evidence=(
                        (
                            f"Recession probability is "
                            f"{recession_probability:.0%}."
                        ),
                    ),
                    risks=(
                        "Growth may remain resilient.",
                        "Financial conditions may ease.",
                    ),
                    affected_asset_classes=(
                        "equities",
                        "high_yield_bonds",
                        "government_bonds",
                    ),
                    expected_duration_months=forecast.horizon_months,
                )
            )

        if (
            stagflation_probability >= 0.20
            and forecast.base_case.scenario
            != EconomicScenario.STAGFLATION
        ):
            themes.append(
                EconomicTheme(
                    identifier="material-inflation-tail-risk",
                    title="Material Inflation Tail Risk",
                    category=ThemeCategory.INFLATION,
                    direction=ThemeDirection.MIXED,
                    confidence=self._weighted_confidence(
                        forecast,
                        stagflation_probability,
                    ),
                    description=(
                        "Persistent inflation is not the base case but "
                        "remains a material alternative scenario."
                    ),
                    supporting_evidence=(
                        (
                            f"Stagflation probability is "
                            f"{stagflation_probability:.0%}."
                        ),
                    ),
                    risks=(
                        "Inflation may continue normalizing.",
                        "Demand weakness may reduce pricing pressure.",
                    ),
                    affected_asset_classes=(
                        "commodities",
                        "government_bonds",
                        "equities",
                    ),
                    expected_duration_months=forecast.horizon_months,
                )
            )

        return themes

    def _weighted_confidence(
        self,
        forecast: EconomicForecast,
        scenario_weight: float,
    ) -> float:
        value = (
            forecast.confidence * 0.60
            + scenario_weight * 0.40
        )

        return self._clamp(value)

    def _state_confidence(
        self,
        forecast: EconomicForecast,
        *,
        adjustment: float,
    ) -> float:
        value = (
            forecast.current_state.confidence
            * adjustment
        )

        return self._clamp(value)

    def _calculate_confidence(
        self,
        *,
        forecast: EconomicForecast,
        themes: list[EconomicTheme],
    ) -> float:
        average_theme_confidence = sum(
            theme.confidence
            for theme in themes
        ) / len(themes)

        value = (
            forecast.confidence * 0.60
            + average_theme_confidence * 0.40
        )

        return self._clamp(value)

    def _build_summary(
        self,
        *,
        forecast: EconomicForecast,
        themes: list[EconomicTheme],
    ) -> str:
        leading_theme = max(
            themes,
            key=lambda theme: theme.confidence,
        )

        return (
            f"{len(themes)} economic themes were identified. "
            f"The leading theme is '{leading_theme.title}', "
            f"while the forecast base case remains "
            f"{forecast.base_case.scenario.value.replace('_', ' ')}."
        )

    def _deduplicate(
        self,
        themes: list[EconomicTheme],
    ) -> list[EconomicTheme]:
        unique: dict[str, EconomicTheme] = {}

        for theme in themes:
            existing = unique.get(theme.identifier)

            if (
                existing is None
                or theme.confidence > existing.confidence
            ):
                unique[theme.identifier] = theme

        return list(unique.values())

    @staticmethod
    def _clamp(value: float) -> float:
        return round(
            max(0.0, min(1.0, value)),
            4,
        )
