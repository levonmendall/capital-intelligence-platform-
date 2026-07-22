"""Federal Reserve Economic Data provider."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


FRED_OBSERVATIONS_URL = (
    "https://api.stlouisfed.org/fred/series/observations"
)


class FREDProviderError(RuntimeError):
    """Raised when FRED data cannot be retrieved or interpreted."""


@dataclass(frozen=True)
class FREDObservation:
    """A single dated economic observation."""

    date: str
    value: float


class FREDProvider:
    """Retrieve economic series from the official FRED API."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 20,
    ) -> None:
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        self.timeout = timeout

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
            response = requests.get(
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
