# ADR-0001: Committee owns collective governance

## Status

Accepted.

## Context

The repository contains two historically distinct committee models:

- `committee.meeting.InvestmentCommittee` evaluates a `CIOBriefing` and records
  narrative meeting opinions.
- `intelligence.investment_committee.InvestmentCommittee` evaluates an
  `InvestmentRecommendation` with specialist assessments, quorum, weighted
  confidence, vetoes, policy thresholds, and a final decision.

Both models are useful, but the second performs collective governance even
though it lives in the analytical `intelligence` package. Continuing to add
callers directly to that location would deepen the ownership mismatch and make
a later migration disruptive.

## Decision

`committee` is the owner of collective governance and final decisions.
`intelligence` owns analytical observations, state, forecasts, themes, theses,
recommendations, specialist assessments, and compatibility facades.

The canonical entry point for recommendation governance is now:

```python
from committee.recommendation_governance import (
    RecommendationInvestmentCommittee,
)
```

The canonical end-to-end entry point is:

```python
from committee.workflow import InstitutionalDecisionWorkflow
```

Existing imports from `intelligence.investment_committee`,
`intelligence.investment_policy`, and related modules remain supported. They
are compatibility paths during incremental migration and are not removed or
behaviorally changed by this decision.

The briefing-oriented committee remains available through
`committee.meeting`. It is a narrative meeting record, not the canonical
recommendation-decision engine. New code must use explicit class names rather
than relying on the ambiguous package-level `committee.InvestmentCommittee`.

## Consequences

- New callers have a stable ownership-correct import path.
- The institutional workflow produces a decision, report, and statistics from
  the same recommendation and timestamp.
- Existing callers and tests continue to work.
- Physical implementation files may move from `intelligence` to `committee`
  later, behind the canonical facade.
- The package-level legacy name remains temporarily ambiguous and should be
  deprecated only after known callers migrate.

## Migration conditions

Physical moves may occur only when:

1. canonical paths have full behavioral tests;
2. repository callers use the canonical paths;
3. compatibility modules re-export the same class objects;
4. circular-import checks pass;
5. removal is announced in a versioned deprecation policy.
