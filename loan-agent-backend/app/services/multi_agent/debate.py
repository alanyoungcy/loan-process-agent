"""
Multi-Agent Debate System
Multiple AI agents debate and vote on optimal collection strategy
Provides higher confidence through consensus and diverse perspectives
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.services.genai.llm_client import get_llm_client
from app.models.case import Case

logger = logging.getLogger(__name__)


class DebateAgent:
    """Single agent in the debate system with specific persona"""

    def __init__(self, name: str, persona: str, expertise: str):
        self.name = name
        self.persona = persona
        self.expertise = expertise
        self.llm_client = get_llm_client()

    async def propose_strategy(
        self,
        case: Case,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Propose a collection strategy from this agent's perspective

        Args:
            case: Case to analyze
            context: Additional context

        Returns:
            Strategy proposal with reasoning
        """
        system_prompt = f"""You are {self.name}, a {self.expertise} expert in debt collection.

YOUR PERSPECTIVE: {self.persona}

Analyze the case and propose the optimal collection strategy.
Consider: effectiveness, compliance, customer relationship, cost-efficiency.

Provide:
1. Recommended strategy
2. Key reasoning points (2-3 bullet points)
3. Expected success rate
4. Potential risks
5. Priority level (1-10)"""

        case_summary = f"""Case Summary:
- Account: {case.case_id}
- Overdue Amount: HK${case.overdue_amount:,.2f}
- Days Overdue: {case.overdue_days}
- Current Status: {case.status}
- Contact Count: {case.contact_count}
- Priority: {case.priority}/10
- Customer Segment: {context.get('customer_segment', 'standard')}
- Previous Strategy: {case.recommended_strategy or 'None'}
"""

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": case_summary}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return {
                "agent": self.name,
                "expertise": self.expertise,
                "proposal": response["content"],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent {self.name} proposal failed: {str(e)}")
            return {
                "agent": self.name,
                "error": str(e)
            }

    async def critique_proposal(
        self,
        proposal: Dict[str, Any],
        case: Case
    ) -> Dict[str, Any]:
        """
        Critique another agent's proposal

        Args:
            proposal: Proposal to critique
            case: Case details

        Returns:
            Critique with agreement level
        """
        system_prompt = f"""You are {self.name}, a {self.expertise} expert.

Review this strategy proposal and provide constructive critique.

Consider:
- Does it align with best practices?
- Are there better alternatives?
- What are potential weaknesses?
- What would you change?

Provide:
1. Agreement level (0-100%)
2. Strengths of the proposal (1-2 points)
3. Concerns or improvements (1-2 points)
4. Your recommendation (support, modify, reject)"""

        critique_prompt = f"""Proposal by {proposal['agent']}:
{proposal['proposal']}

Case: HK${case.overdue_amount:,.2f}, {case.overdue_days} days overdue"""

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": critique_prompt}
                ],
                temperature=0.6,
                max_tokens=400
            )

            return {
                "critic": self.name,
                "proposal_agent": proposal['agent'],
                "critique": response["content"],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent {self.name} critique failed: {str(e)}")
            return {
                "critic": self.name,
                "error": str(e)
            }


class MultiAgentDebate:
    """
    Multi-agent debate system for collection strategy optimization
    Uses diverse perspectives to reach consensus
    """

    def __init__(self):
        self.llm_client = get_llm_client()

        # Initialize agent panel with diverse perspectives
        self.agents = [
            DebateAgent(
                name="Compliance Officer",
                persona="You prioritize regulatory compliance and risk mitigation. You ensure all strategies follow Money Lenders Ordinance and PDPO.",
                expertise="Compliance & Legal"
            ),
            DebateAgent(
                name="Customer Relations Expert",
                persona="You focus on maintaining positive customer relationships and long-term recovery. You believe empathy drives better outcomes.",
                expertise="Customer Experience"
            ),
            DebateAgent(
                name="Data Analyst",
                persona="You rely on historical data and proven metrics. You recommend strategies with highest statistical success rates.",
                expertise="Analytics & Data Science"
            ),
            DebateAgent(
                name="Senior Collector",
                persona="You have 15 years of field experience. You know what works in practice and can read customer situations.",
                expertise="Practical Collection"
            ),
            DebateAgent(
                name="Financial Advisor",
                persona="You consider the customer's financial capacity and design sustainable payment solutions.",
                expertise="Financial Planning"
            )
        ]

    async def debate_strategy(
        self,
        case: Case,
        context: Optional[Dict[str, Any]] = None,
        debate_rounds: int = 2
    ) -> Dict[str, Any]:
        """
        Run multi-agent debate to determine optimal strategy

        Args:
            case: Case to analyze
            context: Additional context
            debate_rounds: Number of debate rounds (default 2)

        Returns:
            Consensus strategy with confidence score
        """
        context = context or {}

        logger.info(f"Starting multi-agent debate for case {case.case_id}")

        # Round 1: All agents propose strategies
        proposals = await self._round_1_proposals(case, context)

        if debate_rounds > 1:
            # Round 2: Agents critique each other's proposals
            critiques = await self._round_2_critiques(proposals, case)
        else:
            critiques = []

        # Synthesize consensus
        consensus = await self._synthesize_consensus(
            case,
            proposals,
            critiques
        )

        return {
            "case_id": case.case_id,
            "debate_rounds": debate_rounds,
            "proposals": proposals,
            "critiques": critiques if debate_rounds > 1 else [],
            "consensus": consensus,
            "confidence": consensus.get("confidence"),
            "debated_at": datetime.utcnow().isoformat()
        }

    async def _round_1_proposals(
        self,
        case: Case,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Round 1: All agents propose strategies"""
        logger.info("Round 1: Agents proposing strategies...")

        # Run all proposals in parallel
        proposal_tasks = [
            agent.propose_strategy(case, context)
            for agent in self.agents
        ]

        proposals = await asyncio.gather(*proposal_tasks)

        # Filter out errors
        valid_proposals = [p for p in proposals if "error" not in p]

        logger.info(f"Received {len(valid_proposals)} valid proposals")

        return valid_proposals

    async def _round_2_critiques(
        self,
        proposals: List[Dict[str, Any]],
        case: Case
    ) -> List[Dict[str, Any]]:
        """Round 2: Agents critique each other"""
        logger.info("Round 2: Agents critiquing proposals...")

        critiques = []

        # Each agent critiques other agents' proposals
        for agent in self.agents:
            for proposal in proposals:
                # Don't critique own proposal
                if proposal["agent"] == agent.name:
                    continue

                critique = await agent.critique_proposal(proposal, case)
                critiques.append(critique)

        logger.info(f"Received {len(critiques)} critiques")

        return critiques

    async def _synthesize_consensus(
        self,
        case: Case,
        proposals: List[Dict[str, Any]],
        critiques: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize consensus from all proposals and critiques

        Args:
            case: Case details
            proposals: All agent proposals
            critiques: All critiques

        Returns:
            Consensus strategy
        """
        logger.info("Synthesizing consensus...")

        # Build synthesis prompt
        proposals_text = "\n\n".join([
            f"**{p['agent']}** ({p['expertise']}):\n{p['proposal']}"
            for p in proposals
        ])

        critiques_text = ""
        if critiques:
            critiques_text = "\n\n".join([
                f"**{c['critic']}** on {c['proposal_agent']}'s proposal:\n{c['critique']}"
                for c in critiques
            ])

        system_prompt = """You are a senior decision maker synthesizing input from multiple experts.

Your task:
1. Identify common themes and consensus points
2. Resolve disagreements by weighing evidence
3. Propose the optimal strategy based on collective wisdom
4. Assign confidence score (0-1) based on agreement level

Output format:
- Recommended Strategy: [name]
- Key Actions: [bullet points]
- Confidence: [0-1 score]
- Reasoning: [brief explanation]
- Dissenting Views: [if any significant disagreement]"""

        synthesis_prompt = f"""Case: HK${case.overdue_amount:,.2f}, {case.overdue_days} days overdue

PROPOSALS:
{proposals_text}

{"CRITIQUES:" if critiques_text else ""}
{critiques_text}

Synthesize the optimal strategy:"""

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.4,  # Lower for final decision
                max_tokens=600
            )

            consensus_text = response["content"]

            # Extract confidence score from text (simple parsing)
            confidence = self._extract_confidence(consensus_text)

            return {
                "strategy": consensus_text,
                "confidence": confidence,
                "num_agents": len(proposals),
                "agreement_level": self._calculate_agreement(proposals, critiques)
            }

        except Exception as e:
            logger.error(f"Consensus synthesis failed: {str(e)}")
            # Fallback: return most common proposal
            return {
                "strategy": proposals[0]["proposal"] if proposals else "No consensus",
                "confidence": 0.5,
                "error": str(e)
            }

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from consensus text"""
        import re

        # Look for patterns like "Confidence: 0.85" or "85%"
        patterns = [
            r'confidence[:\s]+([0-9.]+)',
            r'([0-9]+)%',
            r'score[:\s]+([0-9.]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                # Normalize to 0-1 range
                if value > 1:
                    value = value / 100
                return min(1.0, max(0.0, value))

        # Default confidence if not found
        return 0.7

    def _calculate_agreement(
        self,
        proposals: List[Dict[str, Any]],
        critiques: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate agreement level among agents

        Simple heuristic: more similar proposals = higher agreement
        """
        if len(proposals) <= 1:
            return 1.0

        # Count critiques that recommend "support"
        if critiques:
            support_count = sum(
                1 for c in critiques
                if "support" in c.get("critique", "").lower()
            )
            agreement = support_count / len(critiques) if critiques else 0.5
        else:
            agreement = 0.7  # Default if no critiques

        return agreement


# Singleton instance
_multi_agent_debate: Optional[MultiAgentDebate] = None


def get_multi_agent_debate() -> MultiAgentDebate:
    """Get or create multi-agent debate singleton"""
    global _multi_agent_debate

    if _multi_agent_debate is None:
        _multi_agent_debate = MultiAgentDebate()

    return _multi_agent_debate
