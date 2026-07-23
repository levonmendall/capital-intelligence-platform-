"""Institutional Investment Committee."""

from __future__ import annotations

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
from intelligence.investment_committee_decision import (
    InvestmentCommitteeDecision,
)
from intelligence.recommendation import (
    InvestmentRecommendation,
)


class InvestmentCommittee:
    """
    Coordinates all specialist committee members and
    produces a final institutional decision.
    """

    def __init__(self) -> None:

        self.members = (
            MacroCommitteeMember(),
            RiskCommitteeMember(),
            CreditCommitteeMember(),
            LiquidityCommitteeMember(),
            ValuationCommitteeMember(),
            TechnicalCommitteeMember(),
        )

    def evaluate(
        self,
        recommendation: InvestmentRecommendation,
    ) -> InvestmentCommitteeDecision:

        assessments = tuple(
            member.assess(recommendation)
            for member in self.members
        )

        opinions = tuple(
            assessment.to_opinion()
            for assessment in assessments
        )

        confidence = (
            sum(
                opinion.confidence
                for opinion in opinions
            )
            / len(opinions)
        )

        strengths = tuple(
            {
                item
                for opinion in opinions
                for item in opinion.strengths
            }
        )

        concerns = tuple(
            {
                item
                for opinion in opinions
                for item in opinion.concerns
            }
        )

        suggested_changes = tuple(
            {
                item
                for opinion in opinions
                for item in opinion.suggested_changes
            }
        )

        vetoes = tuple(
            opinion
            for opinion in opinions
            if getattr(opinion.vote, "is_veto", False)
        )

        approved = (
            len(vetoes) == 0
            and confidence >= 0.60
        )

        if approved:
            consensus = "APPROVED"
        elif vetoes:
            consensus = "REJECTED"
        else:
            consensus = "DEFERRED"

        return InvestmentCommitteeDecision(
            recommendation=recommendation,
            consensus=consensus,
            confidence=confidence,
            approved=approved,
            opinions=opinions,
            strengths=strengths,
            concerns=concerns,
            required_changes=suggested_changes,
            vetoes=vetoes,
        )
