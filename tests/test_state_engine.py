from intelligence.observation import (
    Observation,
    ObservationCategory,
    ObservationSet,
    Trend,
    IndicatorId,
)

from intelligence.state import (
    Strength,
    Direction,
)

from intelligence.state_engine import (
    EconomicStateEngine,
)


def test_state_engine_basic():

    observations = ObservationSet()

    observations.add(
        Observation(
            indicator=IndicatorId.GDP.value,
            category=ObservationCategory.GROWTH,
            value=2.4,
            previous_value=2.0,
            trend=Trend.RISING,
        )
    )

    observations.add(
        Observation(
            indicator=IndicatorId.CORE_CPI.value,
            category=ObservationCategory.INFLATION,
            value=2.8,
            previous_value=3.1,
            trend=Trend.FALLING,
        )
    )

    observations.add(
        Observation(
            indicator=IndicatorId.UNEMPLOYMENT.value,
            category=ObservationCategory.LABOR,
            value=4.1,
            previous_value=4.2,
            trend=Trend.STABLE,
        )
    )

    observations.add(
        Observation(
            indicator=IndicatorId.ISM_MANUFACTURING.value,
            category=ObservationCategory.GROWTH,
            value=48.6,
            previous_value=47.8,
            trend=Trend.RISING,
        )
    )

    engine = EconomicStateEngine()

    state = engine.evaluate(observations)

    assert state.growth == Strength.MODERATE
    assert state.inflation == Direction.IMPROVING
    assert state.labor_market == Strength.STRONG
    assert state.manufacturing == Direction.DETERIORATING
    assert state.confidence > 0.0
    assert "Growth appears" in state.summary
