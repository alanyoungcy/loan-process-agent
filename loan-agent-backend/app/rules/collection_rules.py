"""
Loan Collection Business Rules

This module defines all business rules for the loan collection process
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.camunda_dmn.rules_engine import (
    Rule,
    RulePriority,
    RuleResult,
    rules_engine
)


# ============================================================================
# PRIORITY SCORING RULES
# ============================================================================

def priority_high_overdue_amount_condition(facts):
    """Check if overdue amount is high"""
    return facts.get("overdue_amount", 0) > 10000


def priority_high_overdue_amount_action(facts):
    """Increase priority for high overdue amounts"""
    result = RuleResult(rule_name="", executed=True)

    current_priority = facts.get("priority", 5)
    new_priority = min(10, current_priority + 3)

    result.modifications["priority"] = new_priority
    result.actions_taken.append(f"Increased priority from {current_priority} to {new_priority}")
    result.recommendations.append("High value case - prioritize immediate contact")

    return result


def priority_long_overdue_condition(facts):
    """Check if case has been overdue for a long time"""
    return facts.get("overdue_days", 0) > 90


def priority_long_overdue_action(facts):
    """Increase priority for long overdue cases"""
    result = RuleResult(rule_name="", executed=True)

    current_priority = facts.get("priority", 5)
    overdue_days = facts.get("overdue_days", 0)

    # Add 1 point for every 30 days overdue
    increase = min(3, overdue_days // 30)
    new_priority = min(10, current_priority + increase)

    result.modifications["priority"] = new_priority
    result.actions_taken.append(
        f"Increased priority due to {overdue_days} days overdue"
    )

    if overdue_days > 180:
        result.recommendations.append("Consider legal action")
        result.modifications["legal_flag"] = True

    return result


def priority_multiple_contacts_no_response_condition(facts):
    """Check if multiple contact attempts with no response"""
    return (
        facts.get("contact_count", 0) >= 3 and
        facts.get("status") == "new"
    )


def priority_multiple_contacts_no_response_action(facts):
    """Escalate cases with multiple failed contact attempts"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["priority"] = 9
    result.modifications["status"] = "escalated"
    result.actions_taken.append("Escalated due to multiple failed contact attempts")
    result.recommendations.extend([
        "Try alternative contact methods",
        "Consider skip tracing",
        "Review customer contact information"
    ])

    return result


# ============================================================================
# COMPLIANCE RULES
# ============================================================================

def compliance_weekend_contact_restriction_condition(facts):
    """Check if attempting weekend contact"""
    current_time = facts.get("current_time", datetime.now())
    return current_time.weekday() >= 5  # Saturday or Sunday


def compliance_weekend_contact_restriction_action(facts):
    """Block weekend contact attempts"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["can_contact"] = False
    result.actions_taken.append("Blocked weekend contact - compliance violation")
    result.recommendations.append("Schedule contact for next business day")

    return result


def compliance_early_morning_contact_restriction_condition(facts):
    """Check if attempting contact too early"""
    current_time = facts.get("current_time", datetime.now())
    return current_time.hour < 8


def compliance_early_morning_contact_restriction_action(facts):
    """Block early morning contact attempts"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["can_contact"] = False
    result.actions_taken.append("Blocked early morning contact (before 8 AM)")
    result.recommendations.append("Wait until 8 AM for contact")

    return result


def compliance_late_evening_contact_restriction_condition(facts):
    """Check if attempting contact too late"""
    current_time = facts.get("current_time", datetime.now())
    return current_time.hour >= 21


def compliance_late_evening_contact_restriction_action(facts):
    """Block late evening contact attempts"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["can_contact"] = False
    result.actions_taken.append("Blocked late evening contact (after 9 PM)")
    result.recommendations.append("Contact must wait until next business day")

    return result


def compliance_dispute_flag_condition(facts):
    """Check if case has active dispute"""
    return facts.get("dispute_flag", False)


def compliance_dispute_flag_action(facts):
    """Handle cases with active disputes"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["can_contact"] = False
    result.modifications["requires_legal_review"] = True
    result.actions_taken.append("Blocked contact due to active dispute")
    result.recommendations.extend([
        "Route to dispute resolution team",
        "Do not contact customer until dispute resolved",
        "Document all dispute details"
    ])

    return result


# ============================================================================
# COLLECTION STRATEGY RULES
# ============================================================================

def strategy_first_contact_condition(facts):
    """Check if this is the first contact attempt"""
    return facts.get("contact_count", 0) == 0


def strategy_first_contact_action(facts):
    """Set strategy for first contact"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["recommended_scenario"] = "first_contact"
    result.modifications["recommended_tone"] = "professional"
    result.actions_taken.append("Set first contact strategy")
    result.recommendations.extend([
        "Use friendly, professional tone",
        "Verify customer identity",
        "Explain purpose of call clearly",
        "Offer payment options"
    ])

    return result


def strategy_broken_promise_condition(facts):
    """Check if customer broke payment promise"""
    return (
        facts.get("status") == "promised_to_pay" and
        facts.get("promise_date") and
        datetime.fromisoformat(facts.get("promise_date")) < datetime.now()
    )


def strategy_broken_promise_action(facts):
    """Handle broken payment promises"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["status"] = "broken_promise"
    result.modifications["priority"] = min(10, facts.get("priority", 5) + 2)
    result.modifications["recommended_scenario"] = "broken_promise"
    result.modifications["recommended_tone"] = "firm"

    result.actions_taken.append("Detected broken payment promise")
    result.recommendations.extend([
        "Use firmer tone",
        "Emphasize consequences of non-payment",
        "Request immediate payment",
        "Consider payment plan with shorter intervals"
    ])

    return result


def strategy_payment_plan_eligible_condition(facts):
    """Check if customer is eligible for payment plan"""
    return (
        facts.get("overdue_amount", 0) > 1000 and
        facts.get("overdue_amount", 0) < 50000 and
        facts.get("contact_count", 0) > 0 and
        not facts.get("legal_flag", False)
    )


def strategy_payment_plan_eligible_action(facts):
    """Offer payment plan option"""
    result = RuleResult(rule_name="", executed=True)

    overdue_amount = facts.get("overdue_amount", 0)

    # Calculate payment plan options
    plan_6_months = overdue_amount / 6
    plan_12_months = overdue_amount / 12

    result.modifications["payment_plan_eligible"] = True
    result.modifications["payment_plan_options"] = {
        "6_months": round(plan_6_months, 2),
        "12_months": round(plan_12_months, 2)
    }

    result.actions_taken.append("Identified as payment plan eligible")
    result.recommendations.extend([
        f"Offer 6-month plan: ${plan_6_months:.2f}/month",
        f"Offer 12-month plan: ${plan_12_months:.2f}/month",
        "Require 10% down payment",
        "Set up automatic payments"
    ])

    return result


def strategy_legal_action_threshold_condition(facts):
    """Check if case meets legal action threshold"""
    return (
        facts.get("overdue_days", 0) > 180 and
        facts.get("overdue_amount", 0) > 5000 and
        facts.get("contact_count", 0) >= 5
    )


def strategy_legal_action_threshold_action(facts):
    """Recommend legal action"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["legal_flag"] = True
    result.modifications["status"] = "legal_review"
    result.modifications["priority"] = 10

    result.actions_taken.append("Case escalated to legal review")
    result.recommendations.extend([
        "Cease direct collection activity",
        "Send final demand letter",
        "Prepare case documentation for legal team",
        "Review all communication history",
        "Assess cost-benefit of legal action"
    ])

    return result


# ============================================================================
# RISK ASSESSMENT RULES
# ============================================================================

def risk_high_value_customer_condition(facts):
    """Check if customer has high total exposure"""
    return facts.get("customer_total_loans", 0) > 100000


def risk_high_value_customer_action(facts):
    """Handle high-value customers with care"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["requires_supervisor_approval"] = True
    result.modifications["recommended_tone"] = "empathetic"

    result.actions_taken.append("Flagged as high-value customer")
    result.recommendations.extend([
        "Assign to senior collector",
        "Use empathetic approach",
        "Explore relationship preservation options",
        "Consider workout arrangements"
    ])

    return result


def risk_fraud_indicators_condition(facts):
    """Check for fraud indicators"""
    return (
        facts.get("phone_disconnected", False) or
        facts.get("address_invalid", False) or
        facts.get("identity_verification_failed", False)
    )


def risk_fraud_indicators_action(facts):
    """Handle potential fraud cases"""
    result = RuleResult(rule_name="", executed=True)

    result.modifications["fraud_investigation_required"] = True
    result.modifications["can_contact"] = False
    result.modifications["status"] = "fraud_review"

    result.actions_taken.append("Fraud indicators detected")
    result.recommendations.extend([
        "Initiate fraud investigation",
        "Verify customer identity",
        "Review loan origination documents",
        "Check for identity theft indicators",
        "Suspend collection activity pending investigation"
    ])

    return result


# ============================================================================
# REGISTER ALL RULES
# ============================================================================

def initialize_rules():
    """Initialize and register all business rules"""

    # Priority Scoring Rules
    rules_engine.add_rule(Rule(
        name="Priority: High Overdue Amount",
        description="Increase priority for cases with high overdue amounts",
        priority=RulePriority.HIGH,
        condition=priority_high_overdue_amount_condition,
        action=priority_high_overdue_amount_action,
        tags=["priority", "scoring"]
    ))

    rules_engine.add_rule(Rule(
        name="Priority: Long Overdue",
        description="Increase priority for long overdue cases",
        priority=RulePriority.HIGH,
        condition=priority_long_overdue_condition,
        action=priority_long_overdue_action,
        tags=["priority", "scoring"]
    ))

    rules_engine.add_rule(Rule(
        name="Priority: Multiple Failed Contacts",
        description="Escalate cases with multiple failed contact attempts",
        priority=RulePriority.HIGH,
        condition=priority_multiple_contacts_no_response_condition,
        action=priority_multiple_contacts_no_response_action,
        tags=["priority", "escalation"]
    ))

    # Compliance Rules
    rules_engine.add_rule(Rule(
        name="Compliance: Weekend Contact Restriction",
        description="Block contact attempts on weekends",
        priority=RulePriority.HIGHEST,
        condition=compliance_weekend_contact_restriction_condition,
        action=compliance_weekend_contact_restriction_action,
        tags=["compliance", "contact_restrictions"]
    ))

    rules_engine.add_rule(Rule(
        name="Compliance: Early Morning Restriction",
        description="Block contact attempts before 8 AM",
        priority=RulePriority.HIGHEST,
        condition=compliance_early_morning_contact_restriction_condition,
        action=compliance_early_morning_contact_restriction_action,
        tags=["compliance", "contact_restrictions"]
    ))

    rules_engine.add_rule(Rule(
        name="Compliance: Late Evening Restriction",
        description="Block contact attempts after 9 PM",
        priority=RulePriority.HIGHEST,
        condition=compliance_late_evening_contact_restriction_condition,
        action=compliance_late_evening_contact_restriction_action,
        tags=["compliance", "contact_restrictions"]
    ))

    rules_engine.add_rule(Rule(
        name="Compliance: Dispute Flag",
        description="Handle cases with active disputes",
        priority=RulePriority.HIGHEST,
        condition=compliance_dispute_flag_condition,
        action=compliance_dispute_flag_action,
        tags=["compliance", "dispute"]
    ))

    # Collection Strategy Rules
    rules_engine.add_rule(Rule(
        name="Strategy: First Contact",
        description="Set strategy for first contact attempt",
        priority=RulePriority.NORMAL,
        condition=strategy_first_contact_condition,
        action=strategy_first_contact_action,
        tags=["strategy", "contact"]
    ))

    rules_engine.add_rule(Rule(
        name="Strategy: Broken Promise",
        description="Handle broken payment promises",
        priority=RulePriority.HIGH,
        condition=strategy_broken_promise_condition,
        action=strategy_broken_promise_action,
        tags=["strategy", "promise"]
    ))

    rules_engine.add_rule(Rule(
        name="Strategy: Payment Plan Eligible",
        description="Identify payment plan eligible cases",
        priority=RulePriority.NORMAL,
        condition=strategy_payment_plan_eligible_condition,
        action=strategy_payment_plan_eligible_action,
        tags=["strategy", "payment_plan"]
    ))

    rules_engine.add_rule(Rule(
        name="Strategy: Legal Action Threshold",
        description="Recommend legal action for qualifying cases",
        priority=RulePriority.HIGH,
        condition=strategy_legal_action_threshold_condition,
        action=strategy_legal_action_threshold_action,
        tags=["strategy", "legal"]
    ))

    # Risk Assessment Rules
    rules_engine.add_rule(Rule(
        name="Risk: High Value Customer",
        description="Special handling for high-value customers",
        priority=RulePriority.HIGH,
        condition=risk_high_value_customer_condition,
        action=risk_high_value_customer_action,
        tags=["risk", "customer_value"]
    ))

    rules_engine.add_rule(Rule(
        name="Risk: Fraud Indicators",
        description="Detect and handle potential fraud cases",
        priority=RulePriority.HIGHEST,
        condition=risk_fraud_indicators_condition,
        action=risk_fraud_indicators_action,
        tags=["risk", "fraud"]
    ))

    print(f"✅ Initialized {len(rules_engine.rules)} business rules")
