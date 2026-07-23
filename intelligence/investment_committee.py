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
from intelligence.investment_policy import InvestmentPolicy
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class InvestmentCommittee:
    """Coordinate specialist members under an explicit policy."""

    def __init__(
        self,
        members: Iterable[CommitteeMember] | None = None,
        policy: InvestmentPolicy | None = None,
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
            raise ValueError("members cannot be empty")

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

        resolved_policy = policy or InvestmentPolicy()

        if not isinstance(
            resolved_policy,
            InvestmentPolicy,
        ):
            raise TypeError(
                "policy must be an InvestmentPolicy"
            )

        self._members = resolved_members
        self._policy = resolved_policy

    @property
    def members(self) -> tuple[CommitteeMember, ...]:
        """Return the participating specialist members."""

        return self._members

    @property
    def policy(self) -> InvestmentPolicy:
        """Return the governance policy used by the committee."""

        return self._policy

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

        self._enforce_quorum()

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

    def _enforce_quorum(self) -> None:
        if (
            self._policy.require_quorum
            and len(self._members)
            < self._policy.minimum_quorum
        ):
            raise ValueError(
                "Investment Committee quorum not satisfied: "
                f"requires {self._policy.minimum_quorum} members, "
                f"received {len(self._members)}"
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
        if not self._policy.veto_enabled:
            return ()

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

    def _determine_consensus(
        self,
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

        supportive_count = len(
            opinions.supportive
        )

        opposed_count = len(
            opinions.opposed
        )

        neutral_count = len(
            opinions.neutral
        )

        opinion_count = len(
            opinions
        )

        if opposed_count > supportive_count:
            return (
                InvestmentCommitteeConsensus.REJECT
            )

        if (
            self._policy.require_majority_support
            and supportive_count
            <= opinion_count / 2
        ):
            return (
                InvestmentCommitteeConsensus.DEFER
            )

        if (
            neutral_count
            and not self._policy.allow_abstentions
        ):
            return (
                InvestmentCommitteeConsensus.DEFER
            )

        if (
            self._policy.maximum_required_changes
            is not None
            and len(required_changes)
            > self._policy.maximum_required_changes
        ):
            return (
                InvestmentCommitteeConsensus.DEFER
            )

        unanimous_support = (
            supportive_count == opinion_count
        )

        strong_approval_allowed = (
            unanimous_support
            if self._policy
            .require_unanimous_for_strong_approval
            else opposed_count == 0
        )

        if (
            confidence
            >= self._policy
            .minimum_strong_approval_confidence
            and strong_approval_allowed
        ):
            return (
                InvestmentCommitteeConsensus
                .STRONG_APPROVAL
            )

        if (
            confidence
            >= self._policy
            .minimum_approval_confidence
            and opposed_count == 0
        ):
            if required_changes:
                return self._conditional_or_defer()

            return (
                InvestmentCommitteeConsensus.APPROVAL
            )

        if (
            confidence
            >= self._policy
            .minimum_conditional_confidence
            and supportive_count >= opposed_count
        ):
            return self._conditional_or_defer()

        return InvestmentCommitteeConsensus.DEFER

    def _conditional_or_defer(
        self,
    ) -> InvestmentCommitteeConsensus:
        if self._policy.allow_conditional_approval:
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
