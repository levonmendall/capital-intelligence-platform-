# Canonical Institutional Decision Pipeline

## Scope

This document defines the target sequence from evidence to portfolio action.
Only the recommendation-to-committee-result segment is fully orchestrated
today. Unimplemented segments are contracts for future milestones, not claims
of production readiness.

## Sequence

1. Providers retrieve source data and attach provenance.
2. Normalization creates point-in-time observations.
3. Deterministic engines publish typed assessments.
4. Forecasting produces scenarios without changing historical observations.
5. Themes and theses connect evidence to investable implications.
6. Recommendation rules create immutable recommendations.
7. Specialist committee members form independent assessments and opinions.
8. Committee governance applies quorum, weights, vetoes, and policy.
9. Reporting and statistics describe the same final decision.
10. Portfolio construction applies mandate and risk constraints separately.
11. History records inputs, versions, votes, decisions, and outcomes.

## Implemented orchestration boundary

`committee.workflow.InstitutionalDecisionWorkflow` owns steps 7–9 for a single
`InvestmentRecommendation`:

```text
InvestmentRecommendation
    -> RecommendationInvestmentCommittee
    -> RecommendationCommitteeDecision
    -> InvestmentCommitteeReport
    -> CommitteeStatistics
    -> InvestmentCommitteeResult
```

The result enforces that the report references the same decision and that the
workflow timestamp is timezone-aware.

## Non-negotiable boundaries

- Recommendations never execute trades.
- Reports never recalculate or alter decisions.
- Committee approval never bypasses portfolio constraints.
- Portfolio sizing is not a direct transform of an analytical score.
- AI-generated prose never changes deterministic scores or policy.
- Missing or stale data remains visible through confidence and coverage.
- Historical records are append-only and retain the versions used at decision
  time.

## Compatibility

The legacy `intelligence.pipeline` remains the current market-snapshot and
allocation path. It is not silently redirected to the institutional workflow.
Migration requires explicit input adapters, allocation-policy tests, and a
release note because the two flows currently use different regime labels and
decision contracts.
