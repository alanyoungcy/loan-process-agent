"""
Workflow Generator - Generate Workflow Instances
"""
import random
from datetime import datetime, timedelta
from typing import Dict
import uuid


class WorkflowGenerator:
    # Map overdue days to appropriate workflow
    WORKFLOW_MAPPING = {
        (1, 15): "early_stage",
        (16, 30): "standard_collection",
        (31, 90): "standard_collection",
        (91, 180): "standard_collection",
        (181, 365): "legal_escalation"
    }

    WORKFLOW_TASKS = {
        "standard_collection": [
            "initial_contact",
            "send_letter",
            "wait_response",
            "payment_plan",
            "follow_up"
        ],
        "early_stage": [
            "send_sms",
            "wait_3_days",
            "send_email"
        ],
        "payment_plan": [
            "assess_ability",
            "create_plan",
            "monitor_payments"
        ],
        "legal_escalation": [
            "legal_assessment",
            "send_legal_notice"
        ],
        "dispute_resolution": [
            "investigate",
            "resolve_favor"
        ],
        "settlement": [
            "review",
            "negotiate",
            "finalize"
        ]
    }

    def select_workflow(self, overdue_days: int, dispute_flag: bool) -> str:
        """Select appropriate workflow based on case characteristics"""
        if dispute_flag:
            return "dispute_resolution"

        # Payment plan for mid-stage cases with good engagement
        if 30 < overdue_days < 90 and random.random() < 0.3:
            return "payment_plan"

        # Settlement for very late cases
        if overdue_days > 150 and random.random() < 0.1:
            return "settlement"

        # Map based on overdue days
        for (min_days, max_days), workflow in self.WORKFLOW_MAPPING.items():
            if min_days <= overdue_days <= max_days:
                return workflow

        return "standard_collection"

    def get_current_task(self, workflow_key: str, progress: float) -> str:
        """Get current task based on workflow progress"""
        tasks = self.WORKFLOW_TASKS.get(workflow_key, ["initial_contact"])
        task_index = min(int(progress * len(tasks)), len(tasks) - 1)
        return tasks[task_index]

    def generate_instance(self, case_id: str, case_data: Dict) -> Dict:
        """Generate workflow instance for a case"""
        workflow_key = self.select_workflow(
            case_data['overdue_days'],
            case_data.get('dispute_flag', False)
        )

        # Determine if workflow is still running or completed
        is_completed = random.random() < 0.3  # 30% are completed
        status = "completed" if is_completed else "running"

        # Progress through workflow (0.0 to 1.0)
        if is_completed:
            progress = 1.0
        else:
            progress = random.uniform(0.2, 0.8)

        current_task = None if is_completed else self.get_current_task(workflow_key, progress)

        # Started some time after case creation
        started_at = case_data['created_at'] + timedelta(hours=random.randint(1, 48))
        completed_at = None
        if is_completed:
            duration = timedelta(days=random.randint(5, 30))
            completed_at = started_at + duration

        return {
            'id': str(uuid.uuid4()),
            'workflow_key': workflow_key,
            'case_id': case_id,
            'business_key': case_data['case_id'],
            'status': status,
            'current_task_id': current_task,
            'current_task_name': current_task.replace('_', ' ').title() if current_task else None,
            'variables': {
                'overdue_days': case_data['overdue_days'],
                'overdue_amount': case_data['overdue_amount'],
                'contact_attempts': case_data['contact_count'],
                'priority': case_data['priority']
            },
            'started_at': started_at,
            'completed_at': completed_at,
            'updated_at': completed_at or datetime.now()
        }
