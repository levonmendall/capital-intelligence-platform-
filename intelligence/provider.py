"""
Loads market data for the intelligence engine.
"""

import json
from pathlib import Path

from intelligence.models import MarketSnapshot

ROOT = Path(__file__).resolve().parent.parent


def load_sample_snapshot():

    path = ROOT / "config" / "sample_market_snapshot.json"

    with open(path) as file:
        data = json.load(file)

    return MarketSnapshot(
        growth=data["growth"],
        inflation=data["inflation"],
        trend=data["trend"],
        volatility=data["volatility"],
        credit=data["credit"],
    )
