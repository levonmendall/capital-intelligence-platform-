"""Portfolio reporting services for virtual investment mandates."""

from __future__ import annotations

from core.database import get_connection, initialize_database
from core.seed import seed_mandates


def initialize_portfolios() -> None:
    """Initialize the database and seed all configured mandates."""

    initialize_database()
    seed_mandates()


def get_mandates() -> list[dict]:
    """Return all virtual investment mandates."""

    initialize_portfolios()

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


def get_all_mandates() -> list[dict]:
    """Backward-compatible alias for returning all mandates."""

    return get_mandates()


def get_holdings(
    mandate_code: str | None = None,
) -> list[dict]:
    """Return holdings for one mandate or the entire platform."""

    initialize_portfolios()

    query = """
        SELECT
            mandate_code,
            symbol,
            quantity,
            average_cost,
            current_price,
            quantity * average_cost AS cost_basis,
            quantity * current_price AS market_value,
            quantity * (
                current_price - average_cost
            ) AS unrealized_gain,
            updated_at
        FROM holdings
    """

    parameters: list[object] = []

    if mandate_code:
        query += " WHERE mandate_code = ?"
        parameters.append(
            mandate_code.strip().upper()
        )

    query += " ORDER BY mandate_code, symbol"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            tuple(parameters),
        ).fetchall()

    return [dict(row) for row in rows]


def get_trade_history(
    mandate_code: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Return the most recent paper trades."""

    initialize_portfolios()

    query = """
        SELECT
            id,
            created_at,
            mandate_code,
            side,
            symbol,
            quantity,
            price,
            gross_amount,
            rationale
        FROM trades
    """

    parameters: list[object] = []

    if mandate_code:
        query += " WHERE mandate_code = ?"
        parameters.append(
            mandate_code.strip().upper()
        )

    query += """
        ORDER BY id DESC
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        rows = connection.execute(
            query,
            tuple(parameters),
        ).fetchall()

    return [dict(row) for row in rows]


def get_portfolio_snapshots(
    mandate_code: str | None = None,
    limit: int = 250,
) -> list[dict]:
    """Return recent portfolio valuation snapshots."""

    initialize_portfolios()

    query = """
        SELECT
            id,
            created_at,
            mandate_code,
            cash,
            holdings_value,
            nav
        FROM portfolio_snapshots
    """

    parameters: list[object] = []

    if mandate_code:
        query += " WHERE mandate_code = ?"
        parameters.append(
            mandate_code.strip().upper()
        )

    query += """
        ORDER BY id DESC
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        rows = connection.execute(
            query,
            tuple(parameters),
        ).fetchall()

    return [dict(row) for row in rows]


def get_mandate_details(
    mandate_code: str,
) -> dict | None:
    """Return one mandate with holdings, trades, and performance."""

    initialize_portfolios()

    normalized_code = mandate_code.strip().upper()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                code,
                name,
                risk,
                starting_capital,
                cash,
                nav
            FROM mandates
            WHERE code = ?
            """,
            (normalized_code,),
        ).fetchone()

    if row is None:
        return None

    mandate = dict(row)

    starting_capital = float(
        mandate["starting_capital"]
    )
    nav = float(mandate["nav"])

    mandate["total_return"] = (
        (nav / starting_capital) - 1
        if starting_capital
        else 0.0
    )

    mandate["return_pct"] = mandate[
        "total_return"
    ]

    mandate["holdings"] = get_holdings(
        normalized_code
    )

    mandate["trades"] = get_trade_history(
        normalized_code,
        limit=25,
    )

    mandate["snapshots"] = get_portfolio_snapshots(
        normalized_code,
        limit=250,
    )

    return mandate


def get_mandate(
    mandate_code: str,
) -> dict | None:
    """Backward-compatible alias for mandate details."""

    return get_mandate_details(mandate_code)


def get_portfolio_totals() -> dict:
    """Return aggregate values across all mandates."""

    mandates = get_mandates()

    starting_capital = sum(
        float(item["starting_capital"])
        for item in mandates
    )

    cash = sum(
        float(item["cash"])
        for item in mandates
    )

    nav = sum(
        float(item["nav"])
        for item in mandates
    )

    total_return = (
        (nav / starting_capital) - 1
        if starting_capital
        else 0.0
    )

    return {
        "mandate_count": len(mandates),
        "starting_capital": starting_capital,
        "starting": starting_capital,
        "cash": cash,
        "nav": nav,
        "total_return": total_return,
    }


def portfolio_totals() -> dict:
    """Backward-compatible alias for portfolio totals."""

    return get_portfolio_totals()
