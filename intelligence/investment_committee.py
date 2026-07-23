"""Intelligence-layer institutional Investment Committee."""

from __future__ import annotations

from collections.abc import Iterable

from intelligence.committee_member import CommitteeMember
from intelligence.committee_members.credit import (
    CreditCommitteeMember,
)
from intelligence.committee_members.liquidity import (
    LiquidityCommitteeMember,
)
from intelligence.committee_members.macro import (
    MacroCommitteeMember,
)
from intelligence.committee_members.risk import (
    RiskCommitteeMember,
)
from intelligence.committee_members.technical import (
    TechnicalCommitteeMember,
)
from intelligence.committee_members.valuation import (
    ValuationCommitteeMember,
)
from intelligence.committee_opinion import (
    CommitteeOpinion,
    CommitteeOpinionSet,
)
from intelligence.investment_committee_consensus import (
    InvestmentCommitteeConsensus,
)
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class InvestmentCommittee:
    """Coordinate specialist members and produce one final decision."""

    def __init__(
        self,
        members: Iterable[CommitteeMember] | None = None,
    ) -> None:
        resolved_members = tuple(
            members
            if members is not None
            else (
                MacroCommitteeMember(),
                RiskCommitteeMember(),
                CreditCommitteeMember(),
                LiquidityCommitteeMember(),
                ValuationCommitteeMember(),
                TechnicalCommitteeMember(),
            )
        )

        if not resolved_members:
            raise ValueError(
                "members cannot be empty"
            )

        if not all(
            isinstance(member, CommitteeMember)
            for member in resolved_members
        ):
            raise TypeError(
                "members must contain CommitteeMember objects"
            )

        roles = [
            member.role
            for member in resolved_members
        ]

        if len(roles) != len(set(roles)):
            raise ValueError(
                "members cannot contain duplicate committee roles"
            )

        self._members = resolved_members

    @property
    def members(self) -> tuple[CommitteeMember, ...]:
        """Return the participating specialist members."""

        return self._members

    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> InvestmentCommitteeDecision:
        """Evaluate a recommendation across all specialists."""

        if not isinstance(
            recommendation,
            InvestmentRecommendation,
        ):
            raise TypeError(
                "recommendation must be an "
                "InvestmentRecommendation"
            )

        opinions = CommitteeOpinionSet(
            tuple(
                member.evaluate(recommendation)
                for member in self._members
            )
        )

        confidence = self._weighted_confidence(
            opinions
        )

        vetoes = self._collect_vetoes(
            opinions
        )

        strengths = self._unique_items(
            opinion.strengths
            for opinion in opinions
        )

        concerns = self._unique_items(
            opinion.concerns
            for opinion in opinions
        )

        required_changes = self._unique_items(
            opinion.suggested_changes
            for opinion in opinions
        )

        consensus = self._determine_consensus(
            confidence=confidence,
            opinions=opinions,
            vetoes=vetoes,
            required_changes=required_changes,
        )

        return InvestmentCommitteeDecision(
            recommendation=recommendation,
            consensus=consensus,
            confidence=confidence,
            opinions=opinions,
            strengths=strengths,
            concerns=concerns,
            required_changes=required_changes,
            vetoes=vetoes,
        )

    def _weighted_confidence(
        self,
        opinions: CommitteeOpinionSet,
    ) -> float:
        weights = {
            member.role: float(
                member.voting_weight
            )
            for member in self._members
        }

        if any(
            weight <= 0.0
            for weight in weights.values()
        ):
            raise ValueError(
                "voting weights must be greater than zero"
            )

        total_weight = sum(
            weights[opinion.member]
            for opinion in opinions
        )

        weighted_total = sum(
            opinion.confidence
            * weights[opinion.member]
            for opinion in opinions
        )

        return round(
            weighted_total / total_weight,
            4,
        )

    def _collect_vetoes(
        self,
        opinions: CommitteeOpinionSet,
    ) -> tuple[CommitteeOpinion, ...]:
        veto_roles = {
            member.role
            for member in self._members
            if member.has_veto
        }

        return tuple(
            opinion
            for opinion in opinions
            if (
                opinion.member in veto_roles
                and opinion.is_opposed
            )
        )

    @staticmethod
    def _determine_consensus(
        *,
        confidence: float,
        opinions: CommitteeOpinionSet,
        vetoes: tuple[CommitteeOpinion, ...],
        required_changes: tuple[str, ...],
    ) -> InvestmentCommitteeConsensus:
        if vetoes:
            return (
                InvestmentCommitteeConsensus.REJECT
            )

        opposed_count = sum(
            opinion.is_opposed
            for opinion in opinions
        )

        supportive_count = sum(
            opinion.is_supportive
            for opinion in opinions
        )

        if opposed_count > supportive_count:
            return (
                InvestmentCommitteeConsensus.REJECT
            )

        if (
            confidence >= 0.90
            and opposed_count == 0
        ):
            return (
                InvestmentCommitteeConsensus
                .STRONG_APPROVAL
            )

        if (
            confidence >= 0.75
            and opposed_count == 0
        ):
            if required_changes:
                return (
                    InvestmentCommitteeConsensus
                    .APPROVAL_WITH_CONDITIONS
                )

            return (
                InvestmentCommitteeConsensus.APPROVAL
            )

        if (
            confidence >= 0.60
            and supportive_count >= opposed_count
        ):
            return (
                InvestmentCommitteeConsensus
                .APPROVAL_WITH_CONDITIONS
            )

        return InvestmentCommitteeConsensus.DEFER

    @staticmethod
    def _unique_items(
        groups: Iterable[tuple[str, ...]],
    ) -> tuple[str, ...]:
        """Deduplicate while preserving source order."""

        seen: set[str] = set()
        result: list[str] = []

        for group in groups:
            for item in group:
                if item not in seen:
                    seen.add(item)
                    result.append(item)

        return tuple(result)
