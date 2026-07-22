"""SQLite database services for the Capital Intelligence Platform."""

from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = ROOT / "database"
DATABASE_FILE = DATABASE_DIR / "capital_intelligence.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a configured database connection."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the platform database tables."""

    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS mandates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                risk TEXT NOT NULL,
                starting_capital REAL NOT NULL,
                cash REAL NOT NULL,
                nav REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS intelligence_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                regime TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_posture TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                rationale TEXT NOT NULL
            );
            """
        )
