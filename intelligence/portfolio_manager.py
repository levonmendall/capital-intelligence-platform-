"""AI Portfolio Manager for model portfolio recommendations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from intelligence.pipeline import run_intelligence

ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = ROOT / "config" / "model_portfolios.json"


@dataclass(frozen=True)
class TradeRecommendation:
    """A recommended portfolio action."""

    action: str
    symbol: str
    target_weight: float
    rationale: str


def load_model_portfolios() -> dict:
    """Load configured model portfolios."""

    with MODEL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def determine_model(regime: str) -> str:
    """Choose a model portfolio from the market regime."""

    regime = regime.lower()

    if "recession" in regime:
        return "Defensive"

    if "inflation" in regime:
        return "Balanced"

    if "slowdown" in regime:
        return "Balanced"

    return "Growth"


def build_trade_recommendations():
    """Generate AI trade recommendations."""

    decision = run_intelligence(save=False)

    portfolios = load_model_portfolios()

    model_name = determine_model(
        decision.regime
    )

    model = portfolios[model_name]

    recommendations = []

    for symbol, weight in model.items():

        recommendations.append(
            TradeRecommendation(
                action="BUY",
                symbol=symbol,
                target_weight=weight,
                rationale=(
                    f"Selected by the "
                    f"{model_name} model "
                    f"because the current "
                    f"market regime is "
                    f"{decision.regime}."
                ),
            )
        )

    return {
        "model": model_name,
        "regime": decision.regime,
        "confidence": decision.confidence,
        "recommendations": recommendations,
    }
