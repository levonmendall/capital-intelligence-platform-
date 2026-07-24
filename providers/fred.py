"""Federal Reserve Economic Data provider."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from collections.abc import Callable
from typing import Any

import requests

from data import (
    AvailabilityBasis,
    DataQualityState,
    NormalizedObservation,
    ObservationProvenance,
    ObservationQuery,
    ObservationTrend,
    ProviderError,
)


FRED_OBSERVATIONS_URL = (
    "https://api.stlouisfed.org/fred/series/observations"
)


class FREDProviderError(ProviderError):
    """Raised when FRED data cannot be retrieved or interpreted."""


@dataclass(frozen=True)
class FREDObservation:
    """A single dated economic observation."""

    date: str
    value: float
    realtime_start: str | None = None
    realtime_end: str | None = None


class FREDProvider:
    """Retrieve economic series from the official FRED API."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 20,
        *,
        clock: Callable[[], datetime] | None = None,
        http_get: Callable[..., Any] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        self.timeout = timeout
        self._clock = clock or (
            lambda: datetime.now(timezone.utc)
        )
        self._http_get = http_get or requests.get

    @property
    def name(self) -> str:
        """Stable provider identifier."""

        return "FRED"

    @property
    def configured(self) -> bool:
        """Return whether an API key is available."""

        return bool(self.api_key)

    def get_observations(
        self,
        series_id: str,
        limit: int = 24,
        sort_order: str = "desc",
    ) -> list[FREDObservation]:
        """Return recent valid observations for a FRED series."""

        if not self.api_key:
            raise FREDProviderError(
                "FRED_API_KEY is not configured."
            )

        parameters = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
            "sort_order": sort_order,
        }

        try:
            response = self._http_get(
                FRED_OBSERVATIONS_URL,
                params=parameters,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
        except requests.RequestException as error:
            raise FREDProviderError(
                f"FRED request failed for {series_id}: {error}"
            ) from error
        except ValueError as error:
            raise FREDProviderError(
                f"FRED returned invalid JSON for {series_id}."
            ) from error

        observations = []

        for item in payload.get("observations", []):
            raw_value = item.get("value")

            if raw_value in {None, ".", ""}:
                continue

            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                continue

            observations.append(
                FREDObservation(
                    date=str(item["date"]),
                    value=value,
                    realtime_start=(
                        str(item["realtime_start"])
                        if item.get("realtime_start")
                        else None
                    ),
                    realtime_end=(
                        str(item["realtime_end"])
                        if item.get("realtime_end")
                        else None
                    ),
                )
            )

        if not observations:
            raise FREDProviderError(
                f"No usable observations returned for {series_id}."
            )

        return observations

    def get_latest_value(self, series_id: str) -> FREDObservation:
        """Return the latest valid observation."""

        return self.get_observations(
            series_id=series_id,
            limit=12,
            sort_order="desc",
        )[0]

    def fetch(
        self,
        query: ObservationQuery,
    ) -> tuple[NormalizedObservation, ...]:
        """Return canonical observations for a point-in-time query."""

        if not isinstance(query, ObservationQuery):
            raise TypeError("query must be an ObservationQuery")
        if not self.api_key:
            raise FREDProviderError(
                "FRED_API_KEY is not configured."
            )

        retrieved_at = self._clock()
        if (
            not isinstance(retrieved_at, datetime)
            or retrieved_at.tzinfo is None
            or retrieved_at.utcoffset() is None
        ):
            raise FREDProviderError(
                "FRED provider clock must return a "
                "timezone-aware datetime."
            )

        series = query.series
        parameters = {
            "series_id": series.provider_series_identifier,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": query.limit,
            "sort_order": "desc",
            "observation_end": query.as_of.date().isoformat(),
            "vintage_dates": query.as_of.date().isoformat(),
        }

        payload = self._request_payload(
            series.provider_series_identifier,
            parameters,
        )
        observations: list[NormalizedObservation] = []

        for item in payload.get("observations", []):
            value = self._parse_value(item.get("value"))
            if value is None:
                continue

            observation_date = self._parse_date(
                item.get("date"),
                field_name="date",
            )
            if observation_date > query.as_of.date():
                continue

            realtime_start = self._optional_date(
                item.get("realtime_start"),
                field_name="realtime_start",
            )
            released_at, availability_basis = (
                self._availability(
                    realtime_start=realtime_start,
                    retrieved_at=retrieved_at,
                )
            )
            if released_at > query.as_of:
                continue

            observations.append(
                NormalizedObservation(
                    indicator=series.indicator,
                    category=series.category,
                    value=value,
                    unit=series.unit,
                    frequency=series.frequency,
                    observation_date=observation_date,
                    provenance=ObservationProvenance(
                        provider=self.name,
                        series_identifier=(
                            series.provider_series_identifier
                        ),
                        released_at=released_at,
                        retrieved_at=retrieved_at,
                        quality_state=DataQualityState.LIVE,
                        vintage_date=realtime_start,
                        availability_basis=availability_basis,
                    ),
                    transformation=series.transformation,
                    trend=ObservationTrend.UNKNOWN,
                    importance=series.importance,
                    stale_after=series.stale_after,
                )
            )

        if not observations:
            raise FREDProviderError(
                "No point-in-time observations returned for "
                f"{series.provider_series_identifier}."
            )

        return tuple(observations)

    def _request_payload(
        self,
        series_id: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = self._http_get(
                FRED_OBSERVATIONS_URL,
                params=parameters,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise FREDProviderError(
                f"FRED request failed for {series_id}: {error}"
            ) from error
        except ValueError as error:
            raise FREDProviderError(
                f"FRED returned invalid JSON for {series_id}."
            ) from error

        if not isinstance(payload, dict):
            raise FREDProviderError(
                f"FRED returned an invalid payload for {series_id}."
            )
        return payload

    @staticmethod
    def _parse_value(value: object) -> float | None:
        if value in {None, ".", ""}:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_date(
        value: object,
        *,
        field_name: str,
    ) -> date:
        if not isinstance(value, str):
            raise FREDProviderError(
                f"FRED {field_name} must be an ISO date."
            )
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise FREDProviderError(
                f"FRED {field_name} must be an ISO date."
            ) from error

    @classmethod
    def _optional_date(
        cls,
        value: object,
        *,
        field_name: str,
    ) -> date | None:
        if value in {None, ""}:
            return None
        return cls._parse_date(
            value,
            field_name=field_name,
        )

    @staticmethod
    def _availability(
        *,
        realtime_start: date | None,
        retrieved_at: datetime,
    ) -> tuple[datetime, AvailabilityBasis]:
        if realtime_start is None:
            return (
                retrieved_at,
                AvailabilityBasis.RETRIEVAL_PROXY,
            )

        release_at = datetime.combine(
            realtime_start,
            time.max,
            tzinfo=timezone.utc,
        )
        if release_at > retrieved_at:
            return (
                retrieved_at,
                AvailabilityBasis.RETRIEVAL_PROXY,
            )
        return release_at, AvailabilityBasis.PROVIDER_DATE
