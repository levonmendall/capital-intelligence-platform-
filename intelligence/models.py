"""
Data models used by the Capital Intelligence Platform.
"""

from dataclasses import dataclass


@dataclass
class MarketSnapshot:
    growth: float
    inflation: float
    trend: float
    volatility: float
    credit: float


@dataclass
class MarketRegime:
    name: str
    confidence: float
    description: str


@dataclass
class AllocationRecommendation:
    equities: float
    bonds: float
    cash: float
    alternatives: float
