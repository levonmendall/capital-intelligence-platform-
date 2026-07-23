"""
Institutional Investment Policy.

Defines governance rules for Investment Committee decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class InvestmentPolicy:
    """
    Institutional governance policy.

    This object contains the configurable decision thresholds
    used by the Investment Committee.
    """

    minimum_strong_approval_confidence: float = 0.90

    minimum_approval_confidence: float = 0.75

    minimum_conditional_confidence: float = 0.60

    require_unanimous_for_strong_approval: bool = True

    allow_conditional_approval: bool = True

    veto_enabled: bool = True

    require_quorum: bool = True

    minimum_quorum: int = 6

    def __post_init__(self) -> None:

        for field in (
            "minimum_strong_approval_confidence",
            "minimum_approval_confidence",
            "minimum_conditional_confidence",
        ):

            value = getattr(self, field)

            if not isinstance(value, (int, float)):
                raise TypeError(f"{field} must be numeric")

            value = float(value)

            if not isfinite(value):
                raise ValueError(f"{field} must be finite")

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field} must be between 0 and 1"
                )

        if (
            self.minimum_strong_approval_confidence
            < self.minimum_approval_confidence
        ):
            raise ValueError(
                "Strong approval threshold "
                "cannot be below approval threshold."
            )

        if (
            self.minimum_approval_confidence
            < self.minimum_conditional_confidence
        ):
            raise ValueError(
                "Approval threshold "
                "cannot be below conditional threshold."
            )

        if self.minimum_quorum <= 0:
            raise ValueError(
                "minimum_quorum must be positive"
            )
