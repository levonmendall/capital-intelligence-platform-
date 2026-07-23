"""
Institutional Investment Policy.

This module defines the configurable governance rules used by the
Intelligence-layer Investment Committee.

The committee should make decisions according to an InvestmentPolicy
rather than hard-coded thresholds. This allows different institutions
(endowments, pension funds, hedge funds, family offices, etc.) to
operate under different governance rules without changing committee code.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class InvestmentPolicy:
    """
    Configurable governance policy for the Investment Committee.

    Every threshold and governance rule that influences committee
    decisions belongs here rather than inside InvestmentCommittee.
    """

    #
    # Confidence thresholds
    #

    minimum_strong_approval_confidence: float = 0.90

    minimum_approval_confidence: float = 0.75

    minimum_conditional_confidence: float = 0.60

    #
    # Governance rules
    #

    require_unanimous_for_strong_approval: bool = True

    allow_conditional_approval: bool = True

    veto_enabled: bool = True

    require_quorum: bool = True

    minimum_quorum: int = 6

    #
    # Future expansion
    #

    allow_abstentions: bool = False

    require_majority_support: bool = True

    maximum_recommendation_age_days: int = 90

    maximum_required_changes: int | None = None

    def __post_init__(self) -> None:
        """Validate policy configuration."""

        self._validate_thresholds()

        self._validate_quorum()

        self._validate_future_rules()

    def _validate_thresholds(self) -> None:

        for field_name in (
            "minimum_strong_approval_confidence",
            "minimum_approval_confidence",
            "minimum_conditional_confidence",
        ):

            value = getattr(self, field_name)

            if isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be numeric."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{field_name} must be numeric."
                )

            value = float(value)

            if not isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite."
                )

            if value < 0.0 or value > 1.0:
                raise ValueError(
                    f"{field_name} must be between 0 and 1."
                )

        if (
            self.minimum_strong_approval_confidence
            < self.minimum_approval_confidence
        ):
            raise ValueError(
                "Strong approval confidence cannot be less "
                "than approval confidence."
            )

        if (
            self.minimum_approval_confidence
            < self.minimum_conditional_confidence
        ):
            raise ValueError(
                "Approval confidence cannot be less than "
                "conditional approval confidence."
            )

    def _validate_quorum(self) -> None:

        if self.minimum_quorum <= 0:
            raise ValueError(
                "minimum_quorum must be greater than zero."
            )

    def _validate_future_rules(self) -> None:

        if self.maximum_recommendation_age_days <= 0:
            raise ValueError(
                "maximum_recommendation_age_days must be positive."
            )

        if (
            self.maximum_required_changes is not None
            and self.maximum_required_changes < 0
        ):
            raise ValueError(
                "maximum_required_changes cannot be negative."
            )

    @property
    def approval_thresholds(self) -> tuple[float, float, float]:
        """
        Returns the confidence thresholds in descending order.

        (strong approval, approval, conditional approval)
        """

        return (
            self.minimum_strong_approval_confidence,
            self.minimum_approval_confidence,
            self.minimum_conditional_confidence,
        )

    @property
    def uses_vetoes(self) -> bool:
        """Whether vetoes are enforced."""

        return self.veto_enabled

    @property
    def uses_quorum(self) -> bool:
        """Whether quorum is required."""

        return self.require_quorum

    @property
    def requires_unanimous_strong_approval(self) -> bool:
        """Whether strong approval requires unanimous support."""

        return self.require_unanimous_for_strong_approval

    @property
    def supports_conditional_approval(self) -> bool:
        """Whether conditional approvals are permitted."""

        return self.allow_conditional_approval

    def with_overrides(
        self,
        **kwargs,
    ) -> "InvestmentPolicy":
        """
        Create a copy of this policy with one or more fields overridden.

        Example:

            conservative = default_policy.with_overrides(
                minimum_approval_confidence=0.85
            )
        """

        values = {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

        values.update(kwargs)

        return InvestmentPolicy(**values)
