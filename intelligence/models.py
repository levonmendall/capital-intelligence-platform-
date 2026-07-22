"""Structured data models for the intelligence engine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketSnapshot:
    """Normalized market and economic conditions."""

    growth: float
    inflation: float
    trend: float
    volatility: float
    credit: float


@dataclass(frozen=True)
class CIODecision:
    """Explainable investment decision produced by the CIO pipeline."""

    regime: str
    confidence: float
    risk_posture: str
    equities: float
    bonds: float
    cash: float
    alternatives: float
    rationale: str
