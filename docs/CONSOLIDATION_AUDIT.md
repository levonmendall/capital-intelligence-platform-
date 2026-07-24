# Consolidation Audit

## Scope

This audit compared the authoritative repository
`levonmendall/capital-intelligence-platform-` with three supplied archives:

- `Capital_Intelligence_Platform_v3.0.zip`
- `Economic_Regime_Engine_v3.zip`
- `Institutional_Stock_Intelligence_Engine_v1.zip`

The similarly named repository without the trailing hyphen was also inspected
and is treated as a legacy line pending an explicit archival decision.

## Findings

The authoritative repository contained the working foundation:

- `core`, `intelligence`, `committee`, providers, journal, and portfolio-manager
  packages;
- application entry points and configuration;
- automated tests and a GitHub Actions validation workflow.

The supplied platform v3 archive contained 31 files. Most bounded contexts were
empty `__init__.py` files. Its governing documents were one-line summaries, its
stock report engine was an empty future-engine class, and its economic-regime
engine returned a fixed `Transition` result.

The supplied economic-regime v3 archive contained four files. Its engine body
was `pass` and its only test asserted `True`.

The supplied stock-intelligence v1 archive contained ten files. Nine modules
contained only `Future module` docstrings and no analytical implementation.

No supplied archive contained the previously reported 255-test architecture
bridge, compatibility facades, migration notes, or substantive bounded-context
implementations.

## Decision

The archives were not copied over the repository because doing so would replace
working code with placeholders and create a false release history. Their names
and package layout were treated as architectural intent only.

The first consolidation branch instead:

- adds substantive governing documents;
- implements the economic-regime bounded context with deterministic rules,
  explainable signals, confidence, and missing-data coverage;
- adds a compatibility facade without changing the legacy allocation contract;
- updates CI compilation coverage;
- establishes a verified test baseline.

## Verified baseline

The integration branch successfully:

- compiled core domain packages;
- initialized eight mandates;
- ran the existing intelligence pipeline;
- passed 263 automated tests.

The claimed 255-test external package remains unverified and should be audited
separately if a substantive copy is recovered.
