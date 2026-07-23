"""
Committee confidence adjustment engine.

The AdjustmentEngine applies institutional scoring constraints to
committee member adjustments and calculates final confidence.

Committee members propose adjustments. The engine owns:

- single-adjustment limits
- cumulative positive limits
- cumulative negative limits
- confidence clamping
- deterministic rounding
- adjustment audit trails
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from intelligence.committee_adjustment import (
    AdjustmentSet,
    ScoreAdjustment,
)


@dataclass(frozen=True, slots=True)
class AdjustmentPolicy:
    """
    Limits governing committee confidence adjustments.

    Defaults permit normal analytical adjustments while preventing
    one factor or one discipline from overwhelming base confidence.
    """

    maximum_single_adjustment: float = 0.20
    maximum_positive_adjustment: float = 0.30
    maximum_negative_adjustment: float = 0.30

    def __post_init__(self) -> None:
        """Validate policy limits."""

        fields = {
            "maximum_single_adjustment":
                self.maximum_single_adjustment,
            "maximum_positive_adjustment":
                self.maximum_positive_adjustment,
            "maximum_negative_adjustment":
                self.maximum_negative_adjustment,
        }

        for name, value in fields.items():
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be numeric."
                )

            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if not 0.0 <= numeric_value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0."
                )

            object.__setattr__(
                self,
                name,
                round(numeric_value, 4),
            )


@dataclass(frozen=True, slots=True)
class AdjustmentOutcome:
    """
    Result produced by the AdjustmentEngine.
    """

    base_confidence: float
    adjusted_confidence: float
    adjustments: AdjustmentSet

    def __post_init__(self) -> None:
        """Validate confidence values."""

        for name, value in (
            ("base_confidence", self.base_confidence),
            (
                "adjusted_confidence",
                self.adjusted_confidence,
            ),
        ):
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be numeric."
                )

            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0."
                )

        if not isinstance(
            self.adjustments,
            AdjustmentSet,
        ):
            raise TypeError(
                "adjustments must be an AdjustmentSet."
            )


class AdjustmentEngine:
    """
    Applies adjustment policy and calculates final confidence.
    """

    def __init__(
        self,
        policy: AdjustmentPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            if policy is not None
            else AdjustmentPolicy()
        )

    @property
    def policy(self) -> AdjustmentPolicy:
        """Return the active adjustment policy."""

        return self._policy

    def apply(
        self,
        *,
        base_confidence: float,
        adjustments: tuple[ScoreAdjustment, ...],
    ) -> AdjustmentOutcome:
        """
        Apply policy limits to proposed adjustments.

        Adjustments are processed in their supplied order. This makes
        results deterministic and allows committee members to establish
        analytical priority explicitly.
        """

        base_confidence = self.clamp_confidence(
            base_confidence
        )

        if not isinstance(adjustments, tuple):
            raise TypeError(
                "adjustments must be a tuple."
            )

        for adjustment in adjustments:
            if not isinstance(
                adjustment,
                ScoreAdjustment,
            ):
                raise TypeError(
                    "adjustments must contain only "
                    "ScoreAdjustment objects."
                )

        approved: list[ScoreAdjustment] = []

        positive_used = 0.0
        negative_used = 0.0

        for adjustment in adjustments:
            applied_value, reason = (
                self._apply_policy_limits(
                    raw_value=adjustment.raw_value,
                    positive_used=positive_used,
                    negative_used=negative_used,
                )
            )

            if applied_value > 0.0:
                positive_used += applied_value

            elif applied_value < 0.0:
                negative_used += abs(applied_value)

            approved.append(
                adjustment.with_applied_value(
                    applied_value,
                    constraint_reason=reason,
                )
            )

        adjustment_set = AdjustmentSet(
            adjustments=tuple(approved)
        )

        adjusted_confidence = self.clamp_confidence(
            base_confidence
            + adjustment_set.total_applied_adjustment
        )

        return AdjustmentOutcome(
            base_confidence=base_confidence,
            adjusted_confidence=adjusted_confidence,
            adjustments=adjustment_set,
        )

    def _apply_policy_limits(
        self,
        *,
        raw_value: float,
        positive_used: float,
        negative_used: float,
    ) -> tuple[float, str]:
        """Apply single and cumulative adjustment limits."""

        reasons: list[str] = []

        applied_value = raw_value

        single_limit = (
            self._policy.maximum_single_adjustment
        )

        if applied_value > single_limit:
            applied_value = single_limit
            reasons.append(
                "limited by maximum single adjustment"
            )

        elif applied_value < -single_limit:
            applied_value = -single_limit
            reasons.append(
                "limited by maximum single adjustment"
            )

        if applied_value > 0.0:
            positive_remaining = max(
                0.0,
                (
                    self._policy
                    .maximum_positive_adjustment
                    - positive_used
                ),
            )

            if applied_value > positive_remaining:
                applied_value = positive_remaining
                reasons.append(
                    "limited by cumulative positive cap"
                )

        elif applied_value < 0.0:
            negative_remaining = max(
                0.0,
                (
                    self._policy
                    .maximum_negative_adjustment
                    - negative_used
                ),
            )

            if abs(applied_value) > negative_remaining:
                applied_value = -negative_remaining
                reasons.append(
                    "limited by cumulative negative cap"
                )

        return (
            round(applied_value, 4),
            "; ".join(reasons),
        )

    @staticmethod
    def clamp_confidence(
        confidence: float,
    ) -> float:
        """
        Clamp confidence into the valid deterministic range.
        """

        if not isinstance(confidence, (int, float)):
            raise TypeError(
                "confidence must be numeric."
            )

        numeric_confidence = float(confidence)

        if not isfinite(numeric_confidence):
            raise ValueError(
                "confidence must be finite."
            )

        return round(
            max(
                0.0,
                min(
                    1.0,
                    numeric_confidence,
                ),
            ),
            4,
        )
