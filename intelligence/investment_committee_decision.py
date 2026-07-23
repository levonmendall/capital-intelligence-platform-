"""Final decision produced by the intelligence-layer Investment Committee."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeOpinionSet,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)
from intelligence.recommendation import InvestmentRecommendation


@dataclass(frozen=True, slots=True)
class InvestmentCommitteeDecision:
    """Immutable institutional decision for one recommendation."""

    recommendation: InvestmentRecommendation
    consensus: InvestmentCommitteeConsensus
    confidence: float
    opinions: CommitteeOpinionSet
    strengths: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    required_changes: tuple[str, ...] = ()
    vetoes: tuple[CommitteeOpinion, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an InvestmentRecommendation"
            )

        if not isinstance(
            self.consensus,
            InvestmentCommitteeConsensus,
        ):
            raise TypeError(
                "consensus must be an "
                "InvestmentCommitteeConsensus"
            )

        if isinstance(self.confidence, bool) or not isinstance(
            self.confidence,
            (int, float),
        ):
            raise TypeError("confidence must be numeric")

        confidence = float(self.confidence)

        if not isfinite(confidence):
            raise ValueError("confidence must be finite")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(
            self.opinions,
            CommitteeOpinionSet,
        ):
            raise TypeError(
                "opinions must be a CommitteeOpinionSet"
            )

        if (
            self.opinions.recommendation_identifier is not None
            and self.opinions.recommendation_identifier
            != self.recommendation.identifier
        ):
            raise ValueError(
                "opinions must reference the decision recommendation"
            )

        for field_name in (
            "strengths",
            "concerns",
            "required_changes",
        ):
            values = getattr(self, field_name)

            if not isinstance(values, tuple):
                raise TypeError(
                    f"{field_name} must be a tuple"
                )

            if not all(
                isinstance(item, str) and item.strip()
                for item in values
            ):
                raise ValueError(
                    f"{field_name} must contain non-empty strings"
                )

        if not isinstance(self.vetoes, tuple):
            raise TypeError("vetoes must be a tuple")

        if not all(
            isinstance(opinion, CommitteeOpinion)
            for opinion in self.vetoes
        ):
            raise TypeError(
                "vetoes must contain CommitteeOpinion objects"
            )

        if not all(
            opinion.is_opposed
            for opinion in self.vetoes
        ):
            raise ValueError(
                "every veto must be an opposed opinion"
            )

        object.__setattr__(
            self,
            "confidence",
            round(confidence, 4),
        )

    @property
    def approved(self) -> bool:
        """Whether the consensus permits approval."""

        return self.consensus.approved

    @property
    def has_veto(self) -> bool:
        """Whether a veto-capable member blocked approval."""

        return bool(self.vetoes)

    @property
    def opinion_count(self) -> int:
        """Number of specialist opinions included."""

        return len(self.opinions)
