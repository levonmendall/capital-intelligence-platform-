"""Shared test configuration."""

from pathlib import Path

import pytest

import core.database as database


@pytest.fixture(autouse=True)
def isolated_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Use a brand-new temporary SQLite database for every test."""

    database_path = tmp_path / "capital_intelligence_test.db"

    monkeypatch.setattr(
        database,
        "DATABASE_FILE",
        database_path,
    )

    database.initialize_database()

    yield database_path
