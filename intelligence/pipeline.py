"""End-to-end AI CIO decision pipeline."""

from core.database import get_connection, initialize_database
from intelligence.models import CIODecision
from providers.economic_snapshot import load_best_available_snapshot
from intelligence.regime import determine_regime


def build_allocation(regime: str) -> tuple[str, dict[str, float]]:
    """Select a model allocation based on the market regime."""

    if regime in {"Expansion", "Recovery"}:
        return (
            "Constructive",
            {
                "equities": 0.60,
                "bonds": 0.20,
                "cash": 0.10,
                "alternatives": 0.10,
            },
        )

    if regime in {"Recession", "Inflation Shock"}:
        return (
            "Defensive",
            {
                "equities": 0.25,
                "bonds": 0.35,
                "cash": 0.25,
                "alternatives": 0.15,
            },
        )

    return (
        "Balanced",
        {
            "equities": 0.40,
            "bonds": 0.30,
            "cash": 0.20,
            "alternatives": 0.10,
        },
    )


def run_intelligence(save: bool = True) -> CIODecision:
    """Run market analysis and return an explainable CIO decision."""

    snapshot, data_source = load_best_available_snapshot()
    regime, confidence = determine_regime(snapshot)
    risk_posture, allocation = build_allocation(regime)

    rationale = (
    f"The system identified a {regime} regime with "
    f"{confidence:.0%} confidence using {data_source}. "
    f"The resulting posture is {risk_posture.lower()}."
)

    decision = CIODecision(
        regime=regime,
        confidence=confidence,
        risk_posture=risk_posture,
        equities=allocation["equities"],
        bonds=allocation["bonds"],
        cash=allocation["cash"],
        alternatives=allocation["alternatives"],
        rationale=rationale,
    )

    if save:
        save_decision(decision)

    return decision


def save_decision(decision: CIODecision) -> None:
    """Save a CIO decision to the permanent intelligence journal."""

    initialize_database()

    recommendation = (
        f"Equities {decision.equities:.0%}, "
        f"Bonds {decision.bonds:.0%}, "
        f"Cash {decision.cash:.0%}, "
        f"Alternatives {decision.alternatives:.0%}"
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO intelligence_log (
                regime,
                confidence,
                risk_posture,
                recommendation,
                rationale
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                decision.regime,
                decision.confidence,
                decision.risk_posture,
                recommendation,
                decision.rationale,
            ),
        )
