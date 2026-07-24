"""Immutable point-in-time SEC filing and company-fact contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Protocol, runtime_checkable

from data.provider import ProviderError
from data.security import normalize_cik


class FilingProviderError(ProviderError):
    """Base error for filing-provider failures."""


def _required_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _aware_datetime(value: object, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


@dataclass(frozen=True, slots=True)
class FilingQuery:
    """Point-in-time request for accepted SEC filings."""

    cik: str
    as_of: datetime
    forms: tuple[str, ...] = ()
    limit: int = 100

    def __post_init__(self) -> None:
        object.__setattr__(self, "cik", normalize_cik(self.cik))
        _aware_datetime(self.as_of, field_name="as_of")
        if not isinstance(self.forms, tuple):
            raise TypeError("forms must be a tuple")
        normalized_forms = tuple(
            _required_text(form, field_name="form").upper()
            for form in self.forms
        )
        object.__setattr__(self, "forms", normalized_forms)
        if len(normalized_forms) != len(set(normalized_forms)):
            raise ValueError("forms cannot contain duplicates")
        if isinstance(self.limit, bool) or not isinstance(
            self.limit,
            int,
        ):
            raise TypeError("limit must be an int")
        if not 1 <= self.limit <= 10_000:
            raise ValueError("limit must be between 1 and 10000")


@dataclass(frozen=True, slots=True)
class FilingRecord:
    """One SEC filing available at its acceptance timestamp."""

    cik: str
    accession_number: str
    form: str
    accepted_at: datetime
    filing_date: date
    primary_document: str
    retrieved_at: datetime
    report_date: date | None = None
    source_url: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cik", normalize_cik(self.cik))
        for field_name in (
            "accession_number",
            "form",
            "primary_document",
        ):
            value = _required_text(
                getattr(self, field_name),
                field_name=field_name,
            )
            if field_name == "form":
                value = value.upper()
            object.__setattr__(self, field_name, value)
        accepted_at = _aware_datetime(
            self.accepted_at,
            field_name="accepted_at",
        )
        retrieved_at = _aware_datetime(
            self.retrieved_at,
            field_name="retrieved_at",
        )
        if accepted_at > retrieved_at:
            raise ValueError(
                "accepted_at cannot be later than retrieved_at"
            )
        if not isinstance(self.filing_date, date) or isinstance(
            self.filing_date,
            datetime,
        ):
            raise TypeError("filing_date must be a date")
        if self.report_date is not None and (
            not isinstance(self.report_date, date)
            or isinstance(self.report_date, datetime)
        ):
            raise TypeError("report_date must be a date or None")
        if self.source_url is not None:
            object.__setattr__(
                self,
                "source_url",
                _required_text(
                    self.source_url,
                    field_name="source_url",
                ),
            )

    @property
    def is_amendment(self) -> bool:
        """Return whether the filing form is an amendment."""

        return self.form.endswith("/A")


@dataclass(frozen=True, slots=True)
class CompanyFact:
    """One XBRL fact joined to its filing acceptance timestamp."""

    cik: str
    taxonomy: str
    tag: str
    unit: str
    value: float
    period_start: date | None
    period_end: date
    filed_at: date
    accepted_at: datetime
    retrieved_at: datetime
    accession_number: str
    form: str
    fiscal_year: int | None = None
    fiscal_period: str | None = None
    frame: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cik", normalize_cik(self.cik))
        for field_name in (
            "taxonomy",
            "tag",
            "unit",
            "accession_number",
            "form",
        ):
            value = _required_text(
                getattr(self, field_name),
                field_name=field_name,
            )
            if field_name == "form":
                value = value.upper()
            object.__setattr__(self, field_name, value)
        if isinstance(self.value, bool) or not isinstance(
            self.value,
            (int, float),
        ):
            raise TypeError("value must be numeric")
        normalized_value = float(self.value)
        if not isfinite(normalized_value):
            raise ValueError("value must be finite")
        object.__setattr__(self, "value", normalized_value)
        for field_name in ("period_end", "filed_at"):
            value = getattr(self, field_name)
            if not isinstance(value, date) or isinstance(value, datetime):
                raise TypeError(f"{field_name} must be a date")
        if self.period_start is not None and (
            not isinstance(self.period_start, date)
            or isinstance(self.period_start, datetime)
        ):
            raise TypeError("period_start must be a date or None")
        if (
            self.period_start is not None
            and self.period_start > self.period_end
        ):
            raise ValueError(
                "period_start cannot be later than period_end"
            )
        accepted_at = _aware_datetime(
            self.accepted_at,
            field_name="accepted_at",
        )
        retrieved_at = _aware_datetime(
            self.retrieved_at,
            field_name="retrieved_at",
        )
        if accepted_at > retrieved_at:
            raise ValueError(
                "accepted_at cannot be later than retrieved_at"
            )
        if self.fiscal_year is not None:
            if isinstance(self.fiscal_year, bool) or not isinstance(
                self.fiscal_year,
                int,
            ):
                raise TypeError("fiscal_year must be an int or None")
        for field_name in ("fiscal_period", "frame"):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _required_text(value, field_name=field_name),
                )

    @property
    def is_amendment(self) -> bool:
        """Return whether the fact came from an amended form."""

        return self.form.endswith("/A")


@runtime_checkable
class FilingProvider(Protocol):
    """Provider capable of point-in-time filing retrieval."""

    @property
    def name(self) -> str:
        """Stable provider identifier."""

    def fetch_filings(
        self,
        query: FilingQuery,
    ) -> tuple[FilingRecord, ...]:
        """Return filings accepted by the query boundary."""

    def fetch_company_facts(
        self,
        query: FilingQuery,
    ) -> tuple[CompanyFact, ...]:
        """Return XBRL facts accepted by the query boundary."""
