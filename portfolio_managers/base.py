"""Base interface for the eight mandate portfolio managers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from intelligence.cio_guidance import CIOGuidance
from portfolio_managers.response import PortfolioManagerResponse


class PortfolioManager(ABC):
    """Common interface implemented by every mandate manager."""

    manager_id: str
    manager_name: str

    @abstractmethod
    def respond(
        self,
        guidance: CIOGuidance,
        portfolio: Any,
    ) -> PortfolioManagerResponse:
        """Interpret CIO guidance through the manager's mandate."""

        raise NotImplementedError
