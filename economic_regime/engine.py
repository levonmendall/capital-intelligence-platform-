"""Deterministic and explainable economic-regime classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Regime(str, Enum):
    """Economic regimes supported by the institutional classifier."""

    GOLDILOCKS = "Goldilocks"
    REFLATION = "Reflation"
    STAGFLATION = "Stagflation"
    DISINFLATIONARY_SLOWDOWN = "Disinflationary slowdown"
    CONTRACTION = "Contraction"
    TRANSITION = "Transition"


@dataclass(frozen=True)
class EconomicRegimeInputs:
    """Normalized regime inputs.

    Scores use ``[-1, 1]``. Positive growth and liquidity scores are
    supportive. Positive inflation, policy, and stress scores represent
    higher inflation pressure, greater policy restriction, and greater
    financial stress respectively. Missing optional inputs must be ``None``.
    """

    growth: float | None
    inflation: float | None
    policy: float | None = None
    liquidity: float | None = None
    financial_stress: float | None = None

    def __post_init__(self) -> None:
        for name, value in self.as_dict().items():
            if value is not None and not -1.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between -1.0 and 1.0")

    def as_dict(self) -> dict[str, float | None]:
        """Return inputs using stable public signal names."""

        return {
            "growth": self.growth,
            "inflation": self.inflation,
            "policy": self.policy,
            "liquidity": self.liquidity,
            "financial_stress": self.financial_stress,
        }


@dataclass(frozen=True)
class Signal:
    """One auditable signal used by the classifier."""

    name: str
    score: float | None
    assessment: str
    explanation: str


@dataclass(frozen=True)
class EconomicRegimeResult:
    """Complete explainable output from the regime engine."""

    regime: Regime
    confidence: float
    data_coverage: float
    growth_assessment: str
    inflation_assessment: str
    policy_assessment: str
    liquidity_assessment: str
    stress_assessment: str
    strengths: tuple[str, ...]
    risks: tuple[str, ...]
    signals: tuple[Signal, ...]
    conclusion: str


class EconomicRegimeEngine:
    """Classify normalized observations with explicit, testable rules."""

    _SIGNAL_COUNT = 5

    def evaluate(
        self,
        inputs: EconomicRegimeInputs | Mapping[str, float | None],
    ) -> EconomicRegimeResult:
        """Evaluate inputs and return an explainable regime result."""

        normalized = self._coerce_inputs(inputs)
        values = normalized.as_dict()
        coverage = sum(value is not None for value in values.values())
        data_coverage = coverage / self._SIGNAL_COUNT

        growth = normalized.growth or 0.0
        inflation = normalized.inflation or 0.0
        policy = normalized.policy or 0.0
        liquidity = normalized.liquidity or 0.0
        stress = normalized.financial_stress or 0.0

        regime = self._classify(
            growth=growth,
            inflation=inflation,
            policy=policy,
            liquidity=liquidity,
            stress=stress,
            has_growth=normalized.growth is not None,
            has_inflation=normalized.inflation is not None,
        )

        signals = (
            self._signal(
                "growth",
                normalized.growth,
                positive="expanding",
                neutral="stable",
                negative="contracting",
            ),
            self._signal(
                "inflation",
                normalized.inflation,
                positive="elevated",
                neutral="contained",
                negative="disinflationary",
            ),
            self._signal(
                "policy",
                normalized.policy,
                positive="restrictive",
                neutral="neutral",
                negative="accommodative",
            ),
            self._signal(
                "liquidity",
                normalized.liquidity,
                positive="supportive",
                neutral="neutral",
                negative="contracting",
            ),
            self._signal(
                "financial_stress",
                normalized.financial_stress,
                positive="elevated",
                neutral="contained",
                negative="benign",
            ),
        )

        confidence = self._confidence(
            values=values,
            data_coverage=data_coverage,
            regime=regime,
        )
        strengths, risks = self._evidence(signals)

        return EconomicRegimeResult(
            regime=regime,
            confidence=confidence,
            data_coverage=round(data_coverage, 2),
            growth_assessment=signals[0].assessment,
            inflation_assessment=signals[1].assessment,
            policy_assessment=signals[2].assessment,
            liquidity_assessment=signals[3].assessment,
            stress_assessment=signals[4].assessment,
            strengths=strengths,
            risks=risks,
            signals=signals,
            conclusion=self._conclusion(regime, confidence, data_coverage),
        )

    @staticmethod
    def _coerce_inputs(
        inputs: EconomicRegimeInputs | Mapping[str, float | None],
    ) -> EconomicRegimeInputs:
        if isinstance(inputs, EconomicRegimeInputs):
            return inputs
        if not isinstance(inputs, Mapping):
            raise TypeError("inputs must be EconomicRegimeInputs or a mapping")
        return EconomicRegimeInputs(
            growth=inputs.get("growth"),
            inflation=inputs.get("inflation"),
            policy=inputs.get("policy"),
            liquidity=inputs.get("liquidity"),
            financial_stress=inputs.get("financial_stress"),
        )

    @staticmethod
    def _classify(
        *,
        growth: float,
        inflation: float,
        policy: float,
        liquidity: float,
        stress: float,
        has_growth: bool,
        has_inflation: bool,
    ) -> Regime:
        if not has_growth or not has_inflation:
            return Regime.TRANSITION
        if growth <= -0.45 or stress >= 0.75:
            return Regime.CONTRACTION
        if growth <= 0.0 and inflation >= 0.40:
            return Regime.STAGFLATION
        if (
            growth >= 0.30
            and inflation <= 0.25
            and stress < 0.45
            and policy < 0.70
        ):
            return Regime.GOLDILOCKS
        if growth >= 0.25 and inflation > 0.25:
            return Regime.REFLATION
        if growth < 0.30 and inflation <= 0.0:
            return Regime.DISINFLATIONARY_SLOWDOWN
        if liquidity <= -0.70 and policy >= 0.70:
            return Regime.CONTRACTION
        return Regime.TRANSITION

    @staticmethod
    def _signal(
        name: str,
        score: float | None,
        *,
        positive: str,
        neutral: str,
        negative: str,
    ) -> Signal:
        if score is None:
            return Signal(
                name=name,
                score=None,
                assessment="missing",
                explanation=f"No normalized {name.replace('_', ' ')} signal supplied.",
            )
        if score >= 0.25:
            assessment = positive
        elif score <= -0.25:
            assessment = negative
        else:
            assessment = neutral
        return Signal(
            name=name,
            score=score,
            assessment=assessment,
            explanation=(
                f"{name.replace('_', ' ').title()} score {score:+.2f} "
                f"is assessed as {assessment}."
            ),
        )

    @staticmethod
    def _confidence(
        *,
        values: Mapping[str, float | None],
        data_coverage: float,
        regime: Regime,
    ) -> float:
        present = [abs(value) for value in values.values() if value is not None]
        signal_strength = sum(present) / len(present) if present else 0.0
        confidence = 0.45 + (0.30 * data_coverage) + (0.20 * signal_strength)
        if regime == Regime.TRANSITION:
            confidence -= 0.08
        return round(max(0.25, min(0.95, confidence)), 2)

    @staticmethod
    def _evidence(
        signals: tuple[Signal, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        strengths: list[str] = []
        risks: list[str] = []
        for signal in signals:
            if signal.score is None:
                risks.append(
                    f"Missing {signal.name.replace('_', ' ')} data reduces confidence."
                )
            elif signal.name in {"growth", "liquidity"}:
                (strengths if signal.score >= 0.25 else risks).append(
                    signal.explanation
                )
            elif signal.name in {"inflation", "policy", "financial_stress"}:
                (risks if signal.score >= 0.25 else strengths).append(
                    signal.explanation
                )
        return tuple(strengths), tuple(risks)

    @staticmethod
    def _conclusion(
        regime: Regime,
        confidence: float,
        data_coverage: float,
    ) -> str:
        return (
            f"The economy is classified as {regime.value} with "
            f"{confidence:.0%} confidence and {data_coverage:.0%} data coverage. "
            "The classification is deterministic and should be reconsidered "
            "when any supporting signal changes materially."
        )
