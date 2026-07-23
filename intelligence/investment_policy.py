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

from dataclasses import dataclass, fields, replace
from math import isfinite


@dataclass(frozen=True, slots=True)
class InvestmentPolicy:
    """
    Immutable governance policy for the Investment Committee.

    Every business rule that affects committee governance belongs here
    rather than inside InvestmentCommittee.
    """

    #
    # Confidence thresholds
    #

    minimum_strong_approval_confidence: float = 0.90
    minimum_approval_confidence: float = 0.75
    minimum_conditional_confidence: float = 0.60

    #
    # Governance
    #

    require_unanimous_for_strong_approval: bool = True
    allow_conditional_approval: bool = True
    veto_enabled: bool = True

    #
    # Committee participation
    #

    require_quorum: bool = True
    minimum_quorum: int = 6

    allow_abstentions: bool = False
    require_majority_support: bool = True

    #
    # Operational controls
    #

    maximum_recommendation_age_days: int = 90
    maximum_required_changes: int | None = None

    def __post_init__(self) -> None:
        """Validate policy configuration."""

        self._validate_thresholds()
        self._validate_governance()

    #
    # Validation
    #

    def _validate_thresholds(self) -> None:

        threshold_fields = (
            "minimum_strong_approval_confidence",
            "minimum_approval_confidence",
            "minimum_conditional_confidence",
        )

        for field_name in threshold_fields:

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

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0.0 and 1.0."
                )

        if (
            self.minimum_strong_approval_confidence
            < self.minimum_approval_confidence
        ):
            raise ValueError(
                "Strong approval threshold must be greater than "
                "or equal to approval threshold."
            )

        if (
            self.minimum_approval_confidence
            < self.minimum_conditional_confidence
        ):
            raise ValueError(
                "Approval threshold must be greater than or "
                "equal to conditional approval threshold."
            )

    def _validate_governance(self) -> None:

        if self.minimum_quorum <= 0:
            raise ValueError(
                "minimum_quorum must be greater than zero."
            )

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

    #
    # Convenience Properties
    #

    @property
    def approval_thresholds(
        self,
    ) -> tuple[float, float, float]:
        """
        Return confidence thresholds in descending order.

        Returns:
            (
                strong approval,
                approval,
                conditional approval,
            )
        """

        return (
            self.minimum_strong_approval_confidence,
            self.minimum_approval_confidence,
            self.minimum_conditional_confidence,
        )

    @property
    def uses_vetoes(self) -> bool:
        """Whether committee vetoes are enforced."""

        return self.veto_enabled

    @property
    def uses_quorum(self) -> bool:
        """Whether quorum is required."""

        return self.require_quorum

    @property
    def supports_conditional_approval(self) -> bool:
        """Whether conditional approvals are permitted."""

        return self.allow_conditional_approval

    @property
    def requires_unanimous_strong_approval(
        self,
    ) -> bool:
        """Whether strong approval requires unanimity."""

        return (
            self.require_unanimous_for_strong_approval
        )

    #
    # Utility
    #

    def with_overrides(
        self,
        **kwargs,
    ) -> "InvestmentPolicy":
        """
        Create a copy of this policy with one or more values
        overridden.

        Example:
            conservative = policy.with_overrides(
                minimum_approval_confidence=0.85,
                veto_enabled=True,
            )
        """

        valid_fields = {
            field.name
            for field in fields(self)
        }

        invalid = (
            set(kwargs)
            - valid_fields
        )

        if invalid:
            names = ", ".join(sorted(invalid))
            raise ValueError(
                f"Unknown policy fields: {names}"
            )

        return replace(
            self,
            **kwargs,
        )

    def as_dict(self) -> dict[str, object]:
        """
        Return the policy as a dictionary.

        Useful for logging, persistence, configuration
        serialization, and reporting.
        """

        return {
            field.name: getattr(
                self,
                field.name,
            )
            for field in fields(self)
        }

    def describe(self) -> str:
        """
        Produce a concise human-readable description of
        the governance policy.
        """

        return (
            "InvestmentPolicy("
            f"strong={self.minimum_strong_approval_confidence:.2f}, "
            f"approval={self.minimum_approval_confidence:.2f}, "
            f"conditional={self.minimum_conditional_confidence:.2f}, "
            f"vetoes={self.veto_enabled}, "
            f"quorum={self.minimum_quorum}, "
            f"conditional_allowed="
            f"{self.allow_conditional_approval})"
        )
