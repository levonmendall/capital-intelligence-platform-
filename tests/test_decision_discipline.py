"""Tests for thesis, dissent, scenario, and no-action discipline."""

from datetime import datetime, timedelta, timezone

import pytest

from committee import (
    DissentDisposition,
    DissentRegister,
    NoActionDecision,
    NoActionReason,
    StructuredDissent,
)
from intelligence.decision_discipline import (
    CrossAssetTransmissionMap,
    DecisionScenario,
    EvidenceTrustAssessment,
    EvidenceTrustLevel,
    FalsificationTrigger,
    ScenarioShock,
    ShockDirection,
    ThesisLifecycle,
    ThesisLifecycleStatus,
    TransmissionDirection,
    TransmissionEdge,
    TriggerComparator,
    TriggerType,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)


NOW = datetime(2025, 2, 3, 16, 0, tzinfo=timezone.utc)


def invalidation_trigger() -> FalsificationTrigger:
    """Return one deterministic macro falsification trigger."""

    return FalsificationTrigger(
        identifier="real-yield-break",
        trigger_type=TriggerType.MACRO,
        description="Real yields exceed the thesis tolerance",
        metric="US_10Y_REAL_YIELD",
        comparator=TriggerComparator.ABOVE,
        threshold=2.5,
        unit="percent",
    )


def test_thesis_lifecycle_preserves_append_only_transitions() -> None:
    proposed = ThesisLifecycle(
        thesis_identifier="thesis-1",
        status=ThesisLifecycleStatus.PROPOSED,
        opened_at=NOW,
        review_at=NOW + timedelta(days=30),
        falsification_triggers=(invalidation_trigger(),),
    )

    active = proposed.transition(
        ThesisLifecycleStatus.ACTIVE,
        changed_at=NOW + timedelta(hours=1),
        reason="Committee approved the evidence package.",
    )
    challenged = active.transition(
        ThesisLifecycleStatus.CHALLENGED,
        changed_at=NOW + timedelta(days=5),
        reason="Real yields moved toward the invalidation level.",
    )

    assert proposed.status is ThesisLifecycleStatus.PROPOSED
    assert challenged.status is ThesisLifecycleStatus.CHALLENGED
    assert len(challenged.transitions) == 2
    assert challenged.transitions[0].from_status is (
        ThesisLifecycleStatus.PROPOSED
    )


def test_closed_thesis_cannot_be_reactivated() -> None:
    lifecycle = ThesisLifecycle(
        thesis_identifier="thesis-1",
        status=ThesisLifecycleStatus.PROPOSED,
        opened_at=NOW,
        review_at=NOW + timedelta(days=30),
        falsification_triggers=(invalidation_trigger(),),
    ).transition(
        ThesisLifecycleStatus.CLOSED,
        changed_at=NOW + timedelta(hours=1),
        reason="Opportunity no longer exists.",
    )

    with pytest.raises(ValueError, match="cannot transition"):
        lifecycle.transition(
            ThesisLifecycleStatus.ACTIVE,
            changed_at=NOW + timedelta(hours=2),
            reason="Attempted reopening.",
        )


def test_numeric_trigger_requires_threshold() -> None:
    with pytest.raises(ValueError, match="require a threshold"):
        FalsificationTrigger(
            identifier="missing-threshold",
            trigger_type=TriggerType.PRICE,
            description="Price breaks support",
            metric="close",
            comparator=TriggerComparator.BELOW,
        )


def test_evidence_trust_score_is_explicit_and_explainable() -> None:
    trust = EvidenceTrustAssessment(
        evidence_identifier="sec-filing-1",
        source_quality=1.0,
        freshness=0.9,
        completeness=0.8,
        point_in_time_integrity=1.0,
        directness=1.0,
        revision_stability=0.7,
        limitations=("XBRL dimensions are not normalized.",),
    )

    assert trust.score == 0.9
    assert trust.level is EvidenceTrustLevel.HIGH
    assert trust.limitations


def test_cross_asset_map_preserves_direction_and_lag() -> None:
    transmission = CrossAssetTransmissionMap(
        identifier="macro-liquidity-v1",
        version="1.0.0",
        edges=(
            TransmissionEdge(
                source_factor="real_yields",
                target_factor="growth_equity_valuation",
                direction=TransmissionDirection.NEGATIVE,
                strength=0.8,
                expected_lag="days to weeks",
                rationale="Higher discount rates pressure duration.",
            ),
            TransmissionEdge(
                source_factor="real_yields",
                target_factor="bitcoin_liquidity",
                direction=TransmissionDirection.NEGATIVE,
                strength=0.6,
                expected_lag="days",
                rationale="Tighter conditions reduce risk liquidity.",
            ),
        ),
    )

    downstream = transmission.downstream("real_yields")

    assert len(downstream) == 2
    assert downstream[1].target_factor == "bitcoin_liquidity"


def test_scenario_requires_explicit_shocks_and_assumptions() -> None:
    scenario = DecisionScenario(
        identifier="inflation-reacceleration",
        title="Inflation reaccelerates",
        shocks=(
            ScenarioShock(
                factor="inflation",
                direction=ShockDirection.RISE,
                magnitude="100 basis points",
                rationale="Tests duration and liquidity sensitivity.",
            ),
        ),
        assumptions=("Policy rates remain restrictive.",),
    )

    assert scenario.shocks[0].factor == "inflation"


def material_dissent() -> StructuredDissent:
    """Return one open, material committee dissent."""

    return StructuredDissent(
        member="Risk",
        specialty="portfolio risk",
        position="Do not increase exposure.",
        rationale="Liquidity does not support the proposed sizing.",
        evidence_identifiers=("liquidity-score-1",),
        resolution_conditions=(
            "Liquidity score rises above the policy threshold.",
        ),
        materiality=0.8,
        recorded_at=NOW,
    )


def test_dissent_register_preserves_material_minority_view() -> None:
    register = DissentRegister(
        decision_identifier="decision-1",
        majority_view="Increase exposure.",
        dissents=(material_dissent(),),
    )

    assert register.unresolved == register.dissents
    assert register.material_unresolved == register.dissents


def test_resolved_dissent_is_not_reported_as_open() -> None:
    dissent = StructuredDissent(
        member="Credit",
        specialty="credit",
        position="Defer.",
        rationale="Spreads do not confirm the opportunity.",
        evidence_identifiers=("spread-1",),
        resolution_conditions=("Spreads narrow.",),
        materiality=0.6,
        recorded_at=NOW,
        disposition=DissentDisposition.RESOLVED,
    )
    register = DissentRegister(
        decision_identifier="decision-1",
        majority_view="Approve.",
        dissents=(dissent,),
    )

    assert register.unresolved == ()


def test_no_action_is_formal_terminal_committee_outcome() -> None:
    decision = NoActionDecision(
        decision_identifier="decision-1",
        recommendation_identifier="recommendation-1",
        reason=NoActionReason.WAIT_FOR_TRIGGER,
        rationale="Expected return does not compensate current risk.",
        decided_at=NOW,
        review_at=NOW + timedelta(days=7),
        evidence_identifiers=("valuation-1", "risk-1"),
        action_triggers=("Valuation enters the approved range.",),
    )

    consensus = InvestmentCommitteeConsensus.NO_ACTION

    assert decision.action_triggers
    assert not consensus.approved
    assert consensus.terminal
