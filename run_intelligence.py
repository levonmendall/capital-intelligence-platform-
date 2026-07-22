"""Run the Capital Intelligence Platform CIO pipeline."""

from intelligence.pipeline import run_intelligence


def main() -> None:
    """Generate and display the current CIO decision."""

    decision = run_intelligence()

    print("Capital Intelligence Platform")
    print("-----------------------------")
    print(f"Market regime: {decision.regime}")
    print(f"Confidence: {decision.confidence:.0%}")
    print(f"Risk posture: {decision.risk_posture}")
    print()
    print("Recommended allocation")
    print(f"Equities: {decision.equities:.0%}")
    print(f"Bonds: {decision.bonds:.0%}")
    print(f"Cash: {decision.cash:.0%}")
    print(f"Alternatives: {decision.alternatives:.0%}")
    print()
    print(decision.rationale)


if __name__ == "__main__":
    main()
