"""
Economic State Engine.

Transforms normalized observations into an interpretable view of
today's economy.

This layer intentionally contains no forecasting.
"""

from __future__ import annotations

from intelligence.observation import (
    ObservationSet,
    IndicatorId,
    Trend,
)

from intelligence.state import (
    EconomicState,
    Strength,
    Direction,
)


class EconomicStateEngine:
    """
    Produces an EconomicState from normalized observations.
    """

    def evaluate(
        self,
        observations: ObservationSet,
    ) -> EconomicState:

        growth = self._evaluate_growth(observations)

        inflation = self._evaluate_inflation(observations)

        labor = self._evaluate_labor(observations)

        credit = self._evaluate_credit(observations)

        liquidity = self._evaluate_liquidity(observations)

        manufacturing = self._evaluate_manufacturing(
            observations
        )

        housing = self._evaluate_housing(observations)

        consumer = self._evaluate_consumer(observations)

        confidence = self._calculate_confidence(
            observations
        )

        summary = self._build_summary(
            growth=growth,
            inflation=inflation,
            labor=labor,
            credit=credit,
        )

        return EconomicState(
            growth=growth,
            inflation=inflation,
            labor_market=labor,
            credit=credit,
            liquidity=liquidity,
            manufacturing=manufacturing,
            housing=housing,
            consumer=consumer,
            confidence=confidence,
            summary=summary,
        )

    ##########################################################
    # Growth
    ##########################################################

    def _evaluate_growth(
        self,
        observations: ObservationSet,
    ) -> Strength:

        gdp = observations.indicator(
            IndicatorId.GDP.value
        )

        if gdp is None:
            return Strength.MODERATE

        if gdp.value >= 3.0:
            return Strength.STRONG

        if gdp.value >= 1.0:
            return Strength.MODERATE

        return Strength.WEAK

    ##########################################################
    # Inflation
    ##########################################################

    def _evaluate_inflation(
        self,
        observations: ObservationSet,
    ) -> Direction:

        cpi = observations.indicator(
            IndicatorId.CORE_CPI.value
        )

        if cpi is None:
            return Direction.STABLE

        if cpi.trend == Trend.FALLING:
            return Direction.IMPROVING

        if cpi.trend == Trend.RISING:
            return Direction.DETERIORATING

        return Direction.STABLE

    ##########################################################
    # Labor
    ##########################################################

    def _evaluate_labor(
        self,
        observations: ObservationSet,
    ) -> Strength:

        unemployment = observations.indicator(
            IndicatorId.UNEMPLOYMENT.value
        )

        if unemployment is None:
            return Strength.MODERATE

        if unemployment.value <= 4.2:
            return Strength.STRONG

        if unemployment.value <= 5.5:
            return Strength.MODERATE

        return Strength.WEAK

    ##########################################################
    # Credit
    ##########################################################

    def _evaluate_credit(
        self,
        observations: ObservationSet,
    ) -> Direction:

        return Direction.STABLE

    ##########################################################
    # Liquidity
    ##########################################################

    def _evaluate_liquidity(
        self,
        observations: ObservationSet,
    ) -> Direction:

        return Direction.STABLE

    ##########################################################
    # Manufacturing
    ##########################################################

    def _evaluate_manufacturing(
        self,
        observations: ObservationSet,
    ) -> Direction:

        ism = observations.indicator(
            IndicatorId.ISM_MANUFACTURING.value
        )

        if ism is None:
            return Direction.STABLE

        if ism.value >= 50:
            return Direction.IMPROVING

        return Direction.DETERIORATING

    ##########################################################
    # Housing
    ##########################################################

    def _evaluate_housing(
        self,
        observations: ObservationSet,
    ) -> Direction:

        return Direction.STABLE

    ##########################################################
    # Consumer
    ##########################################################

    def _evaluate_consumer(
        self,
        observations: ObservationSet,
    ) -> Strength:

        return Strength.MODERATE

    ##########################################################
    # Confidence
    ##########################################################

    def _calculate_confidence(
        self,
        observations: ObservationSet,
    ) -> float:

        total = len(observations.observations)

        if total >= 30:
            return 0.95

        if total >= 20:
            return 0.90

        if total >= 10:
            return 0.80

        if total >= 5:
            return 0.65

        return 0.50

    ##########################################################
    # Summary
    ##########################################################

    def _build_summary(
        self,
        *,
        growth: Strength,
        inflation: Direction,
        labor: Strength,
        credit: Direction,
    ) -> str:

        return (
            f"Growth appears {growth.value}, "
            f"inflation is {inflation.value}, "
            f"labor markets remain {labor.value}, "
            f"and credit conditions are {credit.value}."
        )
