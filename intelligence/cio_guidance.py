"""Official CIO guidance models."""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.metadata import DocumentMetadata


@dataclass
class ScenarioProbability:
    """Probability assigned to one forward-looking scenario."""

    scenario: str
    probability: float
    horizon_months: int

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ValueError("scenario cannot be empty")

        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(
                "scenario probability must be between 0.0 and 1.0"
            )

        if self.horizon_months < 1:
            raise ValueError("horizon_months must be at least 1")


@dataclass
class ConfidenceScores:
    """Separate measures of confidence and conviction."""

    data_confidence: float
    forecast_confidence: float
    portfolio_conviction: float
    risk_confidence: float

    def __post_init__(self) -> None:
        values = {
            "data_confidence": self.data_confidence,
            "forecast_confidence": self.forecast_confidence,
            "portfolio_conviction": self.portfolio_conviction,
            "risk_confidence": self.risk_confidence,
        }

        for name, value in values.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")


@dataclass
class ChangeCondition:
    """A falsifiable condition that could alter CIO guidance."""

    description: str
    indicator: str | None = None
    comparison: str | None = None
    threshold: float | None = None
    required_periods: int = 1
    severity: str = "review"

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description cannot be empty")

        if self.required_periods < 1:
            raise ValueError("required_periods must be at least 1")


@dataclass
class CIOGuidance:
    """Official strategic guidance distributed to portfolio managers."""

    current_environment: str
    forward_outlook: str
    strategic_guidance: str
    executive_summary: str

    probability_distribution: list[ScenarioProbability]
    confidence: ConfidenceScores

    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)

    opportunities: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    catalysts: list[str] = field(default_factory=list)

    increase_conviction_if: list[ChangeCondition] = field(
        default_factory=list
    )
    reduce_conviction_if: list[ChangeCondition] = field(
        default_factory=list
    )
    change_my_mind_if: list[ChangeCondition] = field(
        default_factory=list
    )

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def __post_init__(self) -> None:
        if not self.current_environment.strip():
            raise ValueError("current_environment cannot be empty")

        if not self.forward_outlook.strip():
            raise ValueError("forward_outlook cannot be empty")

        if not self.probability_distribution:
            raise ValueError(
                "probability_distribution must contain at least one scenario"
            )

        probability_total = sum(
            scenario.probability
            for scenario in self.probability_distribution
        )

        if abs(probability_total - 1.0) > 0.001:
            raise ValueError(
                "scenario probabilities must total 1.0; "
                f"received {probability_total:.4f}"
            )

    def highest_probability_scenario(self) -> ScenarioProbability:
        """Return the CIO's highest-probability forward scenario."""

        return max(
            self.probability_distribution,
            key=lambda scenario: scenario.probability,
        )
