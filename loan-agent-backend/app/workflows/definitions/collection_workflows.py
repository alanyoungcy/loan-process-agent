"""
Collection Workflow Definitions

Predefined BPMN-style workflows for loan collection processes
"""
from app.services.workflows.engine import WorkflowDefinition, workflow_engine
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# STANDARD COLLECTION WORKFLOW
# ============================================================================

standard_collection_workflow = WorkflowDefinition(
    key="standard_collection",
    name="Standard Collection Process",
    description="Standard 30-60-90 day collection workflow",
    version=1,
    tasks=[
        {
            "name": "Initial Contact Attempt",
            "type": "user_task",
            "assignee": None,  # Auto-assigned
            "due_in_days": 3,
            "description": "Make initial contact with customer"
        },
        {
            "name": "Send Initial Letter",
            "type": "service_task",
            "handler_key": "send_collection_letter",
            "due_in_days": 1
        },
        {
            "name": "Follow-up Contact",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 7,
            "description": "Follow up on initial contact"
        },
        {
            "name": "Evaluate Payment Options",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 3,
            "description": "Discuss payment arrangements"
        },
        {
            "name": "Final Notice",
            "type": "service_task",
            "handler_key": "send_final_notice",
            "due_in_days": 1
        },
        {
            "name": "Escalation Decision",
            "type": "user_task",
            "assignee": "supervisor",
            "due_in_days": 2,
            "description": "Decide on escalation to legal"
        }
    ]
)


# ============================================================================
# PAYMENT PLAN WORKFLOW
# ============================================================================

payment_plan_workflow = WorkflowDefinition(
    key="payment_plan",
    name="Payment Plan Management",
    description="Workflow for setting up and monitoring payment plans",
    version=1,
    tasks=[
        {
            "name": "Assess Eligibility",
            "type": "service_task",
            "handler_key": "assess_payment_plan_eligibility",
            "due_in_days": 1
        },
        {
            "name": "Negotiate Terms",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 3,
            "description": "Negotiate payment plan with customer"
        },
        {
            "name": "Generate Agreement",
            "type": "service_task",
            "handler_key": "generate_payment_plan_document",
            "due_in_days": 1
        },
        {
            "name": "Obtain Customer Signature",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 7,
            "description": "Get signed payment plan agreement"
        },
        {
            "name": "Setup Automated Payments",
            "type": "service_task",
            "handler_key": "setup_auto_payments",
            "due_in_days": 1
        },
        {
            "name": "Monitor First Payment",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 30,
            "description": "Verify first payment received"
        }
    ]
)


# ============================================================================
# DISPUTE RESOLUTION WORKFLOW
# ============================================================================

dispute_resolution_workflow = WorkflowDefinition(
    key="dispute_resolution",
    name="Dispute Resolution Process",
    description="Handle customer disputes in compliance with regulations",
    version=1,
    tasks=[
        {
            "name": "Log Dispute",
            "type": "service_task",
            "handler_key": "log_dispute",
            "due_in_days": 1
        },
        {
            "name": "Cease Collection Activity",
            "type": "service_task",
            "handler_key": "cease_collection",
            "due_in_days": 1
        },
        {
            "name": "Send Dispute Acknowledgment",
            "type": "service_task",
            "handler_key": "send_dispute_ack",
            "due_in_days": 5
        },
        {
            "name": "Investigate Dispute",
            "type": "user_task",
            "assignee": "dispute_team",
            "due_in_days": 30,
            "description": "Investigate customer dispute claim"
        },
        {
            "name": "Gather Documentation",
            "type": "user_task",
            "assignee": "dispute_team",
            "due_in_days": 15,
            "description": "Collect supporting documentation"
        },
        {
            "name": "Make Determination",
            "type": "user_task",
            "assignee": "supervisor",
            "due_in_days": 5,
            "description": "Determine validity of dispute"
        },
        {
            "name": "Notify Customer of Decision",
            "type": "service_task",
            "handler_key": "send_dispute_decision",
            "due_in_days": 5
        }
    ]
)


# ============================================================================
# LEGAL ESCALATION WORKFLOW
# ============================================================================

legal_escalation_workflow = WorkflowDefinition(
    key="legal_escalation",
    name="Legal Escalation Process",
    description="Escalate case to legal action",
    version=1,
    tasks=[
        {
            "name": "Legal Review",
            "type": "user_task",
            "assignee": "legal_team",
            "due_in_days": 5,
            "description": "Review case for legal action"
        },
        {
            "name": "Send Demand Letter",
            "type": "service_task",
            "handler_key": "send_demand_letter",
            "due_in_days": 1
        },
        {
            "name": "Wait for Response",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 10,
            "description": "Wait for customer response to demand"
        },
        {
            "name": "Prepare Legal Documents",
            "type": "user_task",
            "assignee": "legal_team",
            "due_in_days": 7,
            "description": "Prepare court filing documents"
        },
        {
            "name": "File Lawsuit",
            "type": "user_task",
            "assignee": "legal_team",
            "due_in_days": 3,
            "description": "File lawsuit with court"
        },
        {
            "name": "Update Case Status",
            "type": "service_task",
            "handler_key": "update_case_legal_status",
            "due_in_days": 1
        }
    ]
)


# ============================================================================
# EARLY STAGE COLLECTION WORKFLOW
# ============================================================================

early_stage_workflow = WorkflowDefinition(
    key="early_stage_collection",
    name="Early Stage Collection (0-30 days)",
    description="Soft touch collection for recently overdue accounts",
    version=1,
    tasks=[
        {
            "name": "Send Friendly Reminder",
            "type": "service_task",
            "handler_key": "send_friendly_reminder",
            "due_in_days": 1
        },
        {
            "name": "Courtesy Call",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 7,
            "description": "Make courtesy reminder call"
        },
        {
            "name": "Offer Payment Options",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 3,
            "description": "Present payment options"
        },
        {
            "name": "Follow-up Email",
            "type": "service_task",
            "handler_key": "send_follow_up_email",
            "due_in_days": 7
        }
    ]
)


# ============================================================================
# SETTLEMENT WORKFLOW
# ============================================================================

settlement_workflow = WorkflowDefinition(
    key="settlement",
    name="Settlement Negotiation",
    description="Workflow for negotiating debt settlement",
    version=1,
    tasks=[
        {
            "name": "Assess Settlement Eligibility",
            "type": "service_task",
            "handler_key": "assess_settlement_eligibility",
            "due_in_days": 1
        },
        {
            "name": "Generate Settlement Offer",
            "type": "service_task",
            "handler_key": "generate_settlement_offer",
            "due_in_days": 1
        },
        {
            "name": "Present Offer to Customer",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 3,
            "description": "Present settlement offer"
        },
        {
            "name": "Negotiate Terms",
            "type": "user_task",
            "assignee": None,
            "due_in_days": 7,
            "description": "Negotiate settlement amount and terms"
        },
        {
            "name": "Supervisor Approval",
            "type": "user_task",
            "assignee": "supervisor",
            "due_in_days": 2,
            "description": "Approve settlement terms"
        },
        {
            "name": "Process Settlement Payment",
            "type": "service_task",
            "handler_key": "process_settlement_payment",
            "due_in_days": 1
        },
        {
            "name": "Send Settlement Letter",
            "type": "service_task",
            "handler_key": "send_settlement_confirmation",
            "due_in_days": 1
        },
        {
            "name": "Close Case",
            "type": "service_task",
            "handler_key": "close_case",
            "due_in_days": 1
        }
    ]
)


def register_all_workflows():
    """Register all workflow definitions with the engine"""
    workflows = [
        standard_collection_workflow,
        dispute_resolution_workflow,
        legal_escalation_workflow,
    ]

    for workflow in workflows:
        workflow_engine.register_workflow(workflow)

    logger.info(f"Registered {len(workflows)} workflow definitions")


# Task handlers (simplified - would be implemented elsewhere)
def send_collection_letter(variables):
    """Handler for sending collection letter"""
    logger.info(f"Sending collection letter for case {variables.get('case_id')}")
    return {"letter_sent": True}


def assess_payment_plan_eligibility(variables):
    """Handler for assessing payment plan eligibility"""
    overdue_amount = variables.get("overdue_amount", 0)
    eligible = 1000 < overdue_amount < 50000
    return {"eligible": eligible}


def log_dispute(variables):
    """Handler for logging dispute"""
    logger.info(f"Dispute logged for case {variables.get('case_id')}")
    return {"dispute_logged": True}


# Register handlers
workflow_engine.register_task_handler("send_collection_letter", send_collection_letter)
workflow_engine.register_task_handler("assess_payment_plan_eligibility", assess_payment_plan_eligibility)
workflow_engine.register_task_handler("log_dispute", log_dispute)
