"""Market-data provider for the foundation release."""

import json
from pathlib import Path

from intelligence.models import MarketSnapshot

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_FILE = ROOT / "config" / "sample_market_snapshot.json"


def load_sample_snapshot() -> MarketSnapshot:
    """Load the sample market snapshot from configuration."""

    with SNAPSHOT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return MarketSnapshot(
        growth=float(data["growth"]),
        inflation=float(data["inflation"]),
        trend=float(data["trend"]),
        volatility=float(data["volatility"]),
        credit=float(data["credit"]),
    )
