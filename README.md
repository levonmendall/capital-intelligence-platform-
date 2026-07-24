# Capital Intelligence Platform

An explainable, AI-assisted investment operating system for disciplined research, portfolio management, and paper trading.

## Current Release

Foundation Version 1.0

The active integration milestone adds a deterministic, explainable
`economic_regime` bounded context while preserving the legacy allocation
interface. See:

- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Data sources and governance](DATA_SOURCES.md)
- [Institutional decision engine](DECISION_ENGINE.md)

## Core Objectives

- Analyze changing market conditions
- Identify probable economic and market regimes
- Produce transparent CIO recommendations
- Manage multiple virtual investment mandates
- Record decisions and supporting rationale
- Measure portfolio performance over time

## Planned Architecture
intelligence = analysis and individual committee judgment
committee = meeting orchestration and collective governance

## Governance Architecture

The governance system is divided into two layers.

### `intelligence`

The `intelligence` package owns analytical judgment produced by individual
committee members. It includes:

- committee assessments
- score adjustments
- adjustment policies
- decision thresholds
- committee roles and votes
- individual committee opinions
- specialized members such as the Macro Committee

### `committee`

The `committee` package owns collective institutional governance. It includes:

- committee meetings
- opinion collection
- quorum
- voting weights
- veto handling
- consensus
- final committee decisions

The intended flow is:

Recommendation
→ Individual committee assessments
→ Individual committee opinions
→ Committee meeting
→ Consensus decision
→ Portfolio action

```text
app.py
initialize.py
run_intelligence.py

core/
intelligence/
dashboard/
config/
database/
economic_regime/
tests/
docs/
.github/workflows/
