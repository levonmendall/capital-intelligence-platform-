"""
Database services for the Capital Intelligence Platform.

This module manages creation of the SQLite database and provides
connections for the rest of the application.
"""

from pathlib import Path
import sqlite3

# Root directory of the project
ROOT = Path(__file__).resolve().parent.parent

# Database location
DATABASE_DIR = ROOT / "database"
DATABASE_FILE = DATABASE_DIR / "capital_intelligence.db"


def get_connection():
    """Return a SQLite connection."""
    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create all required tables if they do not already exist."""

    with get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mandates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT,
                objective TEXT,
                risk_level TEXT,
                starting_capital REAL,
                cash REAL,
                nav REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                regime TEXT,
                confidence REAL,
                recommendation TEXT,
                rationale TEXT
            )
            """
        )

        conn.commit()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
