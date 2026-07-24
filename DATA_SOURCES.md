# Data Sources and Governance

## Principles

Investment conclusions are only as credible as their data lineage. Every input
must retain its provider, series or field identifier, observation date,
retrieval time, frequency, unit, transformation, revision status, and
point-in-time availability. Missing, stale, revised, fixture, and fallback data
must be distinguishable.

## Initial source registry

| Domain | Preferred source | Example data | Frequency | Point-in-time concern |
| --- | --- | --- | --- | --- |
| Macro | FRED / original agency | GDP, CPI, payrolls, unemployment, claims, production, housing | Daily to quarterly | Many series are revised |
| Policy | FRED / central banks | Policy rates, balance sheets, reserves | Daily to weekly | Release timing differs |
| Credit | FRED and licensed market sources | IG/HY spreads, lending standards, defaults, yield curve | Daily to quarterly | Survey and default revisions |
| Market | Licensed price provider | Prices, volume, volatility, breadth | Intraday to daily | Corporate-action adjustment |
| Fundamentals | SEC filings and licensed normalized source | Statements, shares, guidance | Quarterly | Filing time and restatements |
| Company metadata | SEC and licensed reference source | Industry, geography, identifiers | Event-driven | Identifier and taxonomy changes |

FRED is the first production macro adapter because the repository already has a
client and much of the initial regime evidence is available there. FRED does
not cover every institutional requirement and must not become a universal
provider abstraction.

## Required normalized observation fields

- canonical indicator identifier;
- numeric value and unit;
- observation date;
- release or availability timestamp;
- retrieval timestamp;
- provider and provider-series identifier;
- frequency and transformation;
- vintage or revision identifier when available;
- quality state: live, cached, stale, fixture, fallback, or missing;
- optional prior value and normalized score.

These fields are implemented by `data.NormalizedObservation` and
`data.ObservationProvenance`. Point-in-time consumers must call
`is_available_at` or `require_available_at` before using an observation at a
historical decision timestamp.

## FRED adapter

`providers.fred.FREDProvider` implements the canonical observation-provider
protocol. Requests include an observation end date and FRED's documented
[`vintage_dates` snapshot](https://fred.stlouisfed.org/docs/api/fred/series_observations.html)
derived from the query's timezone-aware `as_of` boundary. Canonical series
meaning is stored in
`providers.fred_series.FRED_SERIES`, not embedded in HTTP parsing code.

FRED real-time metadata is date-granular. The adapter therefore treats a
provider vintage date as available at the end of that UTC day. If FRED omits
the vintage date, the retrieval timestamp becomes a conservative availability
proxy and the provenance records `retrieval_proxy`.

## Provider behavior

Providers must use explicit timeouts, bounded retries with backoff, rate-limit
handling, schema validation, and actionable exceptions. Caches use keys that
include provider, series, transformation, vintage, and date range. Freshness is
defined per series rather than globally.

## Point-in-time policy

Backtests may only consume information available at the simulated decision
time. Revised macro history and restated company filings require their original
vintage or an explicit limitation label. When point-in-time data is
unavailable, the backtest must report the resulting bias.

## Missing-data policy

- Missing inputs lower data coverage and confidence.
- Core missing inputs may force a `Transition` or `Unavailable` conclusion.
- Values are never silently imputed.
- Any approved imputation method is versioned and disclosed in the result.
- Fixture and fallback data are labeled in application and report outputs.

## Credentials and licensing

API keys stay in environment variables or GitHub secrets. Source licensing,
redistribution rights, retention limits, and derived-data permissions must be
reviewed before a provider is enabled outside development.
