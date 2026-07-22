"""Portfolio reporting services."""

from __future__ import annotations

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
            float(item["starting_capital"])
            for item in mandates
        ),
        "cash": sum(
            float(item["cash"])
            for item in mandates
        ),
        "nav": sum(
            float(item["nav"])
            for item in mandates
        ),
    }


def get_holdings(
    mandate_code: str | None = None,
) -> list[dict]:
    """Return holdings for one mandate or the full platform."""

    initialize_database()

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

    parameters: tuple[str, ...] = ()

    if mandate_code:
        query += " WHERE mandate_code = ?"
        parameters = (
            mandate_code.strip().upper(),
        )

    query += " ORDER BY mandate_code, symbol"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [dict(row) for row in rows]


def get_trade_history(
    mandate_code: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Return the most recent paper trades."""

    initialize_database()

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

    query += " ORDER BY id DESC LIMIT ?"
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
    """Return one mandate with calculated performance."""

    mandate_code = mandate_code.strip().upper()

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
            (mandate_code,),
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

    mandate["holdings"] = get_holdings(
        mandate_code
    )

    return mandate
