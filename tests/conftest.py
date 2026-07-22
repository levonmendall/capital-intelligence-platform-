"""Shared test configuration."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Use a temporary database during every test."""

    database_path = tmp_path / "capital_intelligence_test.db"

    monkeypatch.setattr(
        "core.database.DATABASE_FILE",
        database_path,
    )

    yield database_path
