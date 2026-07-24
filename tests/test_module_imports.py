"""Repository-wide import smoke tests.

Compilation does not execute module top-level code, so missing decorators,
types, and imports can otherwise remain hidden behind a green test suite.
"""

from __future__ import annotations

import importlib
import pkgutil

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
