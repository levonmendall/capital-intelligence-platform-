"""Repository-wide import smoke tests.

Compilation does not execute module top-level code, so missing decorators,
types, and imports can otherwise remain hidden behind a green test suite.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
import subprocess
import sys

import pytest


PACKAGE_ROOTS = (
    "committee",
    "core",
    "economic_regime",
    "intelligence",
    "journal",
    "portfolio_managers",
    "providers",
)

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def _application_modules() -> tuple[str, ...]:
    module_names: set[str] = set()

    for package_name in PACKAGE_ROOTS:
        package = importlib.import_module(package_name)
        module_names.add(package_name)

        package_path = getattr(package, "__path__", None)
        if package_path is None:
            continue

        module_names.update(
            module.name
            for module in pkgutil.walk_packages(
                package_path,
                prefix=f"{package_name}.",
            )
        )

    return tuple(sorted(module_names))


@pytest.mark.parametrize("module_name", _application_modules())
def test_application_module_imports(module_name: str) -> None:
    """Every application module must import without raising an exception."""

    importlib.import_module(module_name)


@pytest.mark.parametrize("package_name", PACKAGE_ROOTS)
def test_package_imports_in_clean_process(package_name: str) -> None:
    """Package initialization must not depend on prior import order."""

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import {package_name}",
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, (
        f"clean import failed for {package_name}:\n"
        f"{completed.stderr}"
    )
