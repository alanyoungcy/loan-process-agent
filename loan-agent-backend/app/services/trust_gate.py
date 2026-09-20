"""
Trust Gate Service
Routes GenAI outputs based on confidence and risk assessment
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class Decision(str, Enum):
    """Trust gate decision types"""
    AUTO_EXECUTE = "auto_execute"
    HUMAN_REVIEW = "human_review"
    ESCALATE = "escalate"
    BLOCK = "block"


class RiskLevel(str, Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrustGate:
    """
    Trust Gate for GenAI output validation
    Routes outputs based on confidence and risk assessment
    """

    def __init__(self):
        # Confidence thresholds
        self.confidence_thresholds = {
            "high": 0.90,
            "medium": 0.70,
            "low": 0.50
        }

        # Risk scoring weights
        self.risk_weights = {
            "amount": {"high": 100000, "medium": 50000, "low": 10000},
            "overdue_days": {"high": 180, "medium": 90, "low": 30},
        }

    def evaluate(
        self,
        genai_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate GenAI output and determine routing decision

        Args:
            genai_output: GenAI service output with confidence score
            context: Additional context (case data, user role, etc.)

        Returns:
            Dict with decision, risk_level, confidence, reasoning, requires_review
        """
        confidence = genai_output.get("confidence", 0.0)
        risk_level = self._assess_risk(genai_output, context or {})

        # Decision logic based on confidence and risk
        decision = self._determine_decision(confidence, risk_level)
        requires_review = decision in [Decision.HUMAN_REVIEW, Decision.ESCALATE]

        evaluation = {
            "decision": decision.value,
            "confidence": confidence,
            "risk_level": risk_level.value,
            "reasoning": self._generate_reasoning(confidence, risk_level, decision),
            "requires_review": requires_review,
            "evaluated_at": datetime.utcnow().isoformat(),
            "risk_factors": self._get_risk_factors(genai_output, context or {}),
        }

        logger.info(
            f"Trust Gate evaluation: decision={decision.value}, "
            f"confidence={confidence:.2f}, risk={risk_level.value}"
        )

        return evaluation

    def _determine_decision(
        self,
        confidence: float,
        risk_level: RiskLevel
    ) -> Decision:
        """
        Determine routing decision based on confidence and risk

        Decision matrix:
        - High confidence + Low risk = AUTO_EXECUTE
        - High confidence + Medium risk = HUMAN_REVIEW
        - Medium confidence + Low/Medium risk = HUMAN_REVIEW
        - Low confidence = ESCALATE
        - Critical risk = BLOCK or ESCALATE
        """
        if risk_level == RiskLevel.CRITICAL:
            return Decision.BLOCK if confidence < 0.5 else Decision.ESCALATE

        if confidence >= self.confidence_thresholds["high"]:
            if risk_level == RiskLevel.LOW:
                return Decision.AUTO_EXECUTE
            elif risk_level == RiskLevel.MEDIUM:
                return Decision.HUMAN_REVIEW
            else:  # HIGH
                return Decision.ESCALATE

        elif confidence >= self.confidence_thresholds["medium"]:
            if risk_level == RiskLevel.LOW:
                return Decision.HUMAN_REVIEW
            else:  # MEDIUM or HIGH
                return Decision.ESCALATE

        else:  # Low confidence
            return Decision.ESCALATE

    def _assess_risk(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """
        Assess risk level based on output characteristics and context

        Risk factors:
        - Amount involved
        - Action type (legal action, third-party contact, etc.)
        - Customer segment (VIP, sensitive)
        - Overdue days
        - Compliance warnings
        - Previous violations
        """
        risk_score = 0

        # Amount-based risk
        amount = output.get("amount") or context.get("overdue_amount", 0)
        if amount > self.risk_weights["amount"]["high"]:
            risk_score += 3
        elif amount > self.risk_weights["amount"]["medium"]:
            risk_score += 2
        elif amount > self.risk_weights["amount"]["low"]:
            risk_score += 1

        # Overdue days risk
        overdue_days = context.get("overdue_days", 0)
        if overdue_days > self.risk_weights["overdue_days"]["high"]:
            risk_score += 2
        elif overdue_days > self.risk_weights["overdue_days"]["medium"]:
            risk_score += 1

        # Action type risk
        action_type = output.get("action_type", "")
        high_risk_actions = [
            "legal_action",
            "final_notice",
            "third_party_contact",
            "demand_letter",
            "escalation"
        ]
        if action_type in high_risk_actions:
            risk_score += 3

        # Customer segment risk
        segment = context.get("customer_segment", "")
        if segment in ["VIP", "sensitive", "vip"]:
            risk_score += 2
        elif segment == "high_risk":
            risk_score += 1

        # Compliance warnings
        compliance_warnings = output.get("compliance_warnings", [])
        if compliance_warnings:
            risk_score += len(compliance_warnings) * 2

        # Dispute or legal flags
        if context.get("dispute_flag"):
            risk_score += 2
        if context.get("legal_flag"):
            risk_score += 3

        # Priority level
        priority = context.get("priority", 5)
        if priority >= 9:
            risk_score += 2
        elif priority >= 7:
            risk_score += 1

        # Convert score to risk level
        if risk_score >= 8:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _get_risk_factors(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Get list of identified risk factors

        Returns:
            List of risk factor descriptions
        """
        factors = []

        amount = output.get("amount") or context.get("overdue_amount", 0)
        if amount > self.risk_weights["amount"]["high"]:
            factors.append(f"High amount: ${amount:,.2f}")

        overdue_days = context.get("overdue_days", 0)
        if overdue_days > self.risk_weights["overdue_days"]["high"]:
            factors.append(f"Long overdue: {overdue_days} days")

        action_type = output.get("action_type", "")
        if action_type in ["legal_action", "final_notice", "third_party_contact"]:
            factors.append(f"High-risk action: {action_type}")

        segment = context.get("customer_segment", "")
        if segment in ["VIP", "sensitive"]:
            factors.append(f"Sensitive customer segment: {segment}")

        if output.get("compliance_warnings"):
            factors.append(
                f"Compliance warnings: {len(output['compliance_warnings'])}"
            )

        if context.get("dispute_flag"):
            factors.append("Active dispute")

        if context.get("legal_flag"):
            factors.append("Legal proceedings active")

        priority = context.get("priority", 5)
        if priority >= 9:
            factors.append(f"Critical priority: {priority}/10")

        return factors

    def _generate_reasoning(
        self,
        confidence: float,
        risk_level: RiskLevel,
        decision: Decision
    ) -> str:
        """
        Generate human-readable reasoning for decision

        Args:
            confidence: Confidence score
            risk_level: Assessed risk level
            decision: Final decision

        Returns:
            Reasoning string
        """
        reasons = []

        # Confidence assessment
        if confidence < self.confidence_thresholds["low"]:
            reasons.append(f"Low confidence score ({confidence:.1%})")
        elif confidence < self.confidence_thresholds["medium"]:
            reasons.append(f"Below-average confidence ({confidence:.1%})")
        elif confidence < self.confidence_thresholds["high"]:
            reasons.append(f"Moderate confidence ({confidence:.1%})")
        else:
            reasons.append(f"High confidence ({confidence:.1%})")

        # Risk assessment
        if risk_level == RiskLevel.CRITICAL:
            reasons.append("Critical risk factors detected")
        elif risk_level == RiskLevel.HIGH:
            reasons.append("High-risk characteristics present")
        elif risk_level == RiskLevel.MEDIUM:
            reasons.append("Medium-risk factors identified")
        else:
            reasons.append("Low risk profile")

        # Decision explanation
        if decision == Decision.AUTO_EXECUTE:
            prefix = "Safe to auto-execute"
        elif decision == Decision.HUMAN_REVIEW:
            prefix = "Human review required"
        elif decision == Decision.ESCALATE:
            prefix = "Escalation to supervisor required"
        else:  # BLOCK
            prefix = "Action blocked for safety"

        return f"{prefix}: {', '.join(reasons)}"

    def should_auto_execute(self, evaluation: Dict[str, Any]) -> bool:
        """
        Check if output should auto-execute

        Args:
            evaluation: Trust gate evaluation result

        Returns:
            True if safe to auto-execute
        """
        return evaluation["decision"] == Decision.AUTO_EXECUTE.value

    def calculate_review_priority(
        self,
        evaluation: Dict[str, Any]
    ) -> int:
        """
        Calculate priority for review queue (1-10)

        Args:
            evaluation: Trust gate evaluation result

        Returns:
            Priority score (10 = highest)
        """
        risk_priorities = {
            RiskLevel.CRITICAL.value: 10,
            RiskLevel.HIGH.value: 8,
            RiskLevel.MEDIUM.value: 5,
            RiskLevel.LOW.value: 3
        }

        base_priority = risk_priorities.get(evaluation["risk_level"], 5)

        # Adjust for confidence
        confidence = evaluation["confidence"]
        if confidence < 0.3:
            base_priority = min(10, base_priority + 2)
        elif confidence < 0.5:
            base_priority = min(10, base_priority + 1)

        return base_priority


# Singleton instance
_trust_gate: Optional[TrustGate] = None


def get_trust_gate() -> TrustGate:
    """Get or create TrustGate singleton"""
    global _trust_gate

    if _trust_gate is None:
        _trust_gate = TrustGate()

    return _trust_gate
