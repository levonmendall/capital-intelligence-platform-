# Capital Intelligence Platform Architecture

## Purpose

The platform is an explainable investment operating system. Deterministic
engines transform versioned evidence into assessments; committee governance
turns assessments into decisions; portfolio policy determines whether and how
an approved decision may be expressed. Generative AI may explain structured
results, but it may not invent observations, silently change scores, override
policy, or choose unconstrained position sizes.

## Bounded contexts

| Context | Owns | Must not own |
| --- | --- | --- |
| `data` and `providers` | Retrieval, normalization, timestamps, provenance, caching | Investment conclusions |
| `economic_regime` | Economic-regime inputs, rules, signals, result | Portfolio allocation |
| `intelligence` | Assessments, forecasts, themes, recommendations, compatibility facades | Collective governance |
| `committee` | Meetings, quorum, weighted votes, vetoes, consensus, final decision | Source-data retrieval |
| `evaluation` | Comparable factor and composite scores | Realized-performance measurement |
| `reporting` | Rendering immutable analytical and decision results | Recalculation of conclusions |
| `history` | Point-in-time evidence, decisions, versions, audit record | Mutation of historical records |
| `analytics` | Returns, attribution, risk, and decision-quality measurement | Ex-ante recommendations |
| `portfolio` | Mandates, constraints, sizing, risk budgets, rebalancing | Analytical score generation |
| `backtesting` | Walk-forward simulation and bias controls | Live order execution |
| `api` and `dashboard` | Application delivery and input validation | Domain rules |

Only contexts implemented in the repository are importable today. The
remaining names are architectural targets and should be added incrementally,
with tests and a real domain contract rather than placeholder packages.

## Dependency direction

1. Domain models and deterministic rules must not depend on the dashboard,
   database, network clients, or report renderers.
2. Providers may depend on external services and normalize their responses into
   domain inputs.
3. Intelligence engines may consume normalized inputs but may not call user
   interfaces.
4. Committee governance consumes immutable recommendations and assessments.
5. Portfolio construction consumes approved decisions plus portfolio state and
   mandate constraints.
6. Reporting consumes results from any layer but never changes them.

Cycles between bounded contexts are prohibited. Cross-context communication
uses explicit immutable models, not shared mutable dictionaries.

## Economic-regime integration

`economic_regime` is the canonical institutional classifier. Its inputs are
normalized to `[-1, 1]`, its rules are deterministic, and its result contains
the regime, confidence, data coverage, component assessments, supporting and
contradicting evidence, signals, and conclusion.

`intelligence.regime.determine_regime` remains the legacy allocation interface.
`intelligence.regime.evaluate_economic_regime` is the compatibility facade for
new consumers. The legacy interface will not be removed until its allocation
consumers have migrated and a deprecation release has been completed.

## Versioning and auditability

Every persisted recommendation and decision should eventually include:

- observation and analysis timestamps;
- provider and series identifiers;
- input snapshot identifier;
- scoring-policy version;
- model or rule-set version;
- committee-policy version;
- code release or commit identifier;
- missing-data and confidence metadata.

Historical records are append-only. Corrections create a new version linked to
the prior record.

## Security and reliability

- Secrets are supplied through environment or secret stores and never committed.
- Provider payloads are untrusted input and require validation.
- Network failures use explicit stale-data or unavailable states.
- A fallback dataset must be labeled; it must never appear as live data.
- Financial actions remain paper-only until authentication, authorization,
  mandate enforcement, idempotency, and an approval boundary are implemented.
- CI must compile domain packages and run the full automated test suite.

## Acceptance rule for new contexts

A new bounded context is accepted only when it has a documented contract,
domain models, deterministic behavior, meaningful tests, compatibility impact
analysis, and no placeholder-only modules.
