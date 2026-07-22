"""Paper-trading services for virtual investment mandates."""

from __future__ import annotations

from dataclasses import dataclass

from core.database import get_connection, initialize_database
from core.seed import seed_mandates


class TradingError(ValueError):
    """Raised when a requested paper trade is invalid."""


@dataclass(frozen=True)
class TradeResult:
    """Result returned after a successful paper trade."""

    trade_id: int
    mandate_code: str
    side: str
    symbol: str
    quantity: float
    price: float
    gross_amount: float
    remaining_cash: float


def normalize_symbol(symbol: str) -> str:
    """Return a clean uppercase ticker symbol."""

    normalized = symbol.strip().upper()

    if not normalized:
        raise TradingError("A ticker symbol is required.")

    return normalized


def place_trade(
    mandate_code: str,
    side: str,
    symbol: str,
    quantity: float,
    price: float,
    rationale: str = "",
) -> TradeResult:
    """Execute a buy or sell inside a virtual mandate."""

    initialize_database()
    seed_mandates()

    mandate_code = mandate_code.strip().upper()
    side = side.strip().upper()
    symbol = normalize_symbol(symbol)
    quantity = float(quantity)
    price = float(price)

    if side not in {"BUY", "SELL"}:
        raise TradingError("Trade side must be BUY or SELL.")

    if quantity <= 0:
        raise TradingError("Trade quantity must be greater than zero.")

    if price <= 0:
        raise TradingError("Trade price must be greater than zero.")

    gross_amount = quantity * price

    with get_connection() as connection:
        mandate = connection.execute(
            """
            SELECT code, cash
            FROM mandates
            WHERE code = ?
            """,
            (mandate_code,),
        ).fetchone()

        if mandate is None:
            raise TradingError(
                f"Unknown investment mandate: {mandate_code}"
            )

        holding = connection.execute(
            """
            SELECT quantity, average_cost
            FROM holdings
            WHERE mandate_code = ? AND symbol = ?
            """,
            (mandate_code, symbol),
        ).fetchone()

        current_quantity = (
            float(holding["quantity"])
            if holding is not None
            else 0.0
        )

        current_average_cost = (
            float(holding["average_cost"])
            if holding is not None
            else 0.0
        )

        current_cash = float(mandate["cash"])

        if side == "BUY":
            if gross_amount > current_cash:
                raise TradingError(
                    "The mandate does not have enough cash "
                    "to complete this paper trade."
                )

            new_quantity = current_quantity + quantity

            new_average_cost = (
                (
                    current_quantity * current_average_cost
                    + gross_amount
                )
                / new_quantity
            )

            new_cash = current_cash - gross_amount

            connection.execute(
                """
                INSERT INTO holdings (
                    mandate_code,
                    symbol,
                    quantity,
                    average_cost,
                    current_price,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(mandate_code, symbol)
                DO UPDATE SET
                    quantity = excluded.quantity,
                    average_cost = excluded.average_cost,
                    current_price = excluded.current_price,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    mandate_code,
                    symbol,
                    new_quantity,
                    new_average_cost,
                    price,
                ),
            )

        else:
            if current_quantity < quantity:
                raise TradingError(
                    "The mandate does not own enough shares "
                    "to complete this sale."
                )

            new_quantity = current_quantity - quantity
            new_cash = current_cash + gross_amount

            if new_quantity == 0:
                connection.execute(
                    """
                    DELETE FROM holdings
                    WHERE mandate_code = ? AND symbol = ?
                    """,
                    (mandate_code, symbol),
                )
            else:
                connection.execute(
                    """
                    UPDATE holdings
                    SET
                        quantity = ?,
                        current_price = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE mandate_code = ? AND symbol = ?
                    """,
                    (
                        new_quantity,
                        price,
                        mandate_code,
                        symbol,
                    ),
                )

        cursor = connection.execute(
            """
            INSERT INTO trades (
                mandate_code,
                side,
                symbol,
                quantity,
                price,
                gross_amount,
                rationale
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mandate_code,
                side,
                symbol,
                quantity,
                price,
                gross_amount,
                rationale.strip(),
            ),
        )

        connection.execute(
            """
            UPDATE mandates
            SET cash = ?
            WHERE code = ?
            """,
            (new_cash, mandate_code),
        )

        trade_id = int(cursor.lastrowid)

    refresh_mandate_nav(mandate_code)

    return TradeResult(
        trade_id=trade_id,
        mandate_code=mandate_code,
        side=side,
        symbol=symbol,
        quantity=quantity,
        price=price,
        gross_amount=gross_amount,
        remaining_cash=new_cash,
    )


def update_holding_price(
    mandate_code: str,
    symbol: str,
    price: float,
) -> None:
    """Update the current paper-market price of a holding."""

    price = float(price)

    if price <= 0:
        raise TradingError("Price must be greater than zero.")

    mandate_code = mandate_code.strip().upper()
    symbol = normalize_symbol(symbol)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE holdings
            SET
                current_price = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE mandate_code = ? AND symbol = ?
            """,
            (price, mandate_code, symbol),
        )

        if cursor.rowcount == 0:
            raise TradingError(
                f"{mandate_code} does not own {symbol}."
            )

    refresh_mandate_nav(mandate_code)


def refresh_mandate_nav(mandate_code: str) -> float:
    """Recalculate and store a mandate's net asset value."""

    mandate_code = mandate_code.strip().upper()

    with get_connection() as connection:
        mandate = connection.execute(
            """
            SELECT cash
            FROM mandates
            WHERE code = ?
            """,
            (mandate_code,),
        ).fetchone()

        if mandate is None:
            raise TradingError(
                f"Unknown investment mandate: {mandate_code}"
            )

        holdings = connection.execute(
            """
            SELECT
                COALESCE(
                    SUM(quantity * current_price),
                    0
                ) AS holdings_value
            FROM holdings
            WHERE mandate_code = ?
            """,
            (mandate_code,),
        ).fetchone()

        cash = float(mandate["cash"])
        holdings_value = float(holdings["holdings_value"])
        nav = cash + holdings_value

        connection.execute(
            """
            UPDATE mandates
            SET nav = ?
            WHERE code = ?
            """,
            (nav, mandate_code),
        )

        connection.execute(
            """
            INSERT INTO portfolio_snapshots (
                mandate_code,
                cash,
                holdings_value,
                nav
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                mandate_code,
                cash,
                holdings_value,
                nav,
            ),
        )

    return nav
