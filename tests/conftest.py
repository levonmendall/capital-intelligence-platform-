"""Shared test configuration."""

from pathlib import Path

import pytest

import core.database as database
from core.seed import seed_mandates


@pytest.fixture(autouse=True)
def isolated_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Create and seed a temporary database for every test."""

    database_path = tmp_path / "capital_intelligence_test.db"

    monkeypatch.setattr(
        database,
        "DATABASE_FILE",
        database_path,
    )

    database.initialize_database()
    seed_mandates()

    yield database_path
