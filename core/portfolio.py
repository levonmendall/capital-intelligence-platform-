"""Portfolio reporting services."""

from core.database import get_connection, initialize_database
from core.seed import seed_mandates


def get_mandates() -> list[dict]:
    """Return all virtual investment mandates."""

    initialize_database()
    seed_mandates()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                code,
                name,
                risk,
                starting_capital,
                cash,
                nav
            FROM mandates
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_portfolio_totals() -> dict:
    """Return aggregate values across all mandates."""

    mandates = get_mandates()

    return {
        "mandate_count": len(mandates),
        "starting_capital": sum(
            float(mandate["starting_capital"]) for mandate in mandates
        ),
        "cash": sum(float(mandate["cash"]) for mandate in mandates),
        "nav": sum(float(mandate["nav"]) for mandate in mandates),
    }
