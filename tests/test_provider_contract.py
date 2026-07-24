"""Tests for provider-neutral observation retrieval contracts."""

from datetime import datetime, timedelta, timezone

import pytest

from data import (
    DataFrequency,
    ObservationQuery,
    SeriesSpecification,
)


def make_series() -> SeriesSpecification:
    return SeriesSpecification(
        provider_series_identifier="UNRATE",
        indicator="unemployment",
        category="labor",
        unit="percent",
        frequency=DataFrequency.MONTHLY,
        stale_after=timedelta(days=45),
        importance=0.9,
    )


def test_series_specification_is_normalized() -> None:
    series = SeriesSpecification(
        provider_series_identifier=" UNRATE ",
        indicator=" unemployment ",
        category=" labor ",
        unit=" percent ",
        frequency=DataFrequency.MONTHLY,
    )

    assert series.provider_series_identifier == "UNRATE"
    assert series.indicator == "unemployment"


def test_series_specification_rejects_invalid_identity() -> None:
    with pytest.raises(ValueError, match="indicator"):
        SeriesSpecification(
            provider_series_identifier="UNRATE",
            indicator="",
            category="labor",
            unit="percent",
            frequency=DataFrequency.MONTHLY,
        )


def test_query_requires_aware_timestamp_and_bounded_limit() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ObservationQuery(
            series=make_series(),
            as_of=datetime(2026, 7, 15),
        )

    with pytest.raises(ValueError, match="limit"):
        ObservationQuery(
            series=make_series(),
            as_of=datetime(
                2026,
                7,
                15,
                tzinfo=timezone.utc,
            ),
            limit=0,
        )


def test_query_preserves_point_in_time_boundary() -> None:
    as_of = datetime(
        2026,
        7,
        15,
        12,
        tzinfo=timezone.utc,
    )
    query = ObservationQuery(
        series=make_series(),
        as_of=as_of,
        limit=12,
    )

    assert query.as_of == as_of
    assert query.limit == 12
