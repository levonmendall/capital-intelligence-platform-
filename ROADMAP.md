# Capital Intelligence Platform Roadmap

## Current release

Foundation 1.x is the validated baseline in GitHub. The active milestone is
repository consolidation and economic-regime integration.

## Milestone 1 — Consolidated foundation

- [x] Identify the authoritative GitHub repository.
- [x] Audit external architecture, regime, and stock packages.
- [x] Reject placeholder packages as release inputs.
- [x] Add governing architecture, roadmap, data, and decision documents.
- [x] Add an explainable economic-regime bounded context.
- [x] Preserve the legacy allocation interface through a compatibility facade.
- [ ] Establish the CI baseline on the integration pull request.

Acceptance: the full repository test suite passes; no working implementation is
replaced by a placeholder; the pull request documents the observed baseline.

## Architecture stabilization

- [x] Establish `committee` as the owner of collective governance.
- [x] Add an ownership-correct recommendation-governance facade.
- [x] Add a canonical recommendation-to-result workflow.
- [x] Preserve existing intelligence imports during migration.
- [x] Document the distinction between briefing meetings and recommendation
  governance.
- [ ] Migrate repository callers to canonical committee imports.
- [ ] Move implementation files only after compatibility paths are proven.
- [ ] Add observation provenance and append-only decision persistence.

## Milestone 2 — Economic-regime productionization

- Map normalized provider observations to regime inputs.
- Add observation dates, vintages, and provider provenance.
- Add point-in-time fixtures for representative historical regimes.
- Calibrate and version thresholds without look-ahead data.
- Add regime-transition tests and committee consumption.
- Render Markdown, JSON, and HTML regime reports.

Acceptance: at least one historically representative fixture exists for every
supported regime, classifications are reproducible, and missing data cannot
produce false precision.

## Milestone 3 — Data foundation

- [x] Define strict normalized observation and provenance models.
- [x] Add point-in-time availability and revision identity.
- [x] Add explicit live, cached, stale, fixture, fallback, and missing states.
- [x] Preserve the legacy state-engine observation contract with an adapter.
- [ ] Define provider protocols.
- Implement resilient FRED retrieval with caching, rate-limit handling,
  freshness rules, and local fixtures.
- Persist observation time, release time, revision/vintage, unit, frequency,
  transformation, and provenance.
- Add deterministic fallback and data-quality policies.

Acceptance: tests run without network access and live data is never confused
with cached, fixture, or fallback data.

## Milestone 4 — Macro and market engines

Implement, in order:

1. Global liquidity
2. Business cycle
3. Credit cycle
4. Market breadth
5. Valuation
6. Technical and momentum
7. Risk

Each engine must publish a typed result with score, confidence, coverage,
evidence, risks, and versioned rules.

## Milestone 5 — Institutional market decision

- Normalize engine results.
- Produce separate opportunity, risk, confidence, and data-quality scores.
- Configure and version weights.
- Apply missing-data and veto policies.
- Submit assessments to committee governance.

## Milestone 6 — Stock intelligence

- Build normalized company and financial-statement models.
- Add quality, financial strength, growth, earnings quality, valuation,
  momentum, regime-fit, and company-risk engines.
- Generate an institutional stock report.
- Add comparison, ranking, screening, and watchlists.

The uploaded stock v1 archive is a specification scaffold, not an
implementation baseline.

## Milestone 7 — Portfolio and validation

- Add constrained position sizing, risk budgets, concentration controls,
  rebalancing, and paper trading.
- Add walk-forward backtests, point-in-time fundamentals, survivorship-bias
  controls, transaction costs, benchmarks, and attribution.

## Milestone 8 — Application

- Provide FastAPI endpoints and a dashboard for assessments, reports,
  committee decisions, portfolios, and history.
- Add authentication, authorization, monitoring, alerts, and deployment.
