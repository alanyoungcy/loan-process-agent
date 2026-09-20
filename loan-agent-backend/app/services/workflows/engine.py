"""
Workflow Engine - BPMN-inspired workflow orchestration

Python-based workflow engine inspired by Camunda for managing
collection process workflows, task assignments, and escalations.
"""
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Workflow task status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStatus(Enum):
    """Workflow instance status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    id: str
    name: str
    task_type: str  # user_task, service_task, script_task
    status: TaskStatus = TaskStatus.PENDING
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    variables: Dict[str, Any] = field(default_factory=dict)

    # Task definition
    handler: Optional[Callable] = None
    condition: Optional[Callable] = None


@dataclass
class WorkflowInstance:
    """Running instance of a workflow"""
    id: str
    workflow_key: str
    status: WorkflowStatus
    business_key: str  # e.g., case_id
    variables: Dict[str, Any] = field(default_factory=dict)
    tasks: List[WorkflowTask] = field(default_factory=list)
    current_task: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Workflow process definition"""
    key: str
    name: str
    description: str
    version: int
    tasks: List[Dict[str, Any]]  # Task definitions
    enabled: bool = True


class WorkflowEngine:
    """
    Workflow orchestration engine

    Manages workflow definitions, instances, and task execution
    """

    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[str, Callable] = {}

    def register_workflow(self, definition: WorkflowDefinition):
        """Register a workflow definition"""
        self.definitions[definition.key] = definition
        logger.info(f"Workflow registered: {definition.key} v{definition.version}")

    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type"""
        self.task_handlers[task_type] = handler
        logger.info(f"Task handler registered: {task_type}")

    def start_workflow(
        self,
        workflow_key: str,
        business_key: str,
        variables: Dict[str, Any] = None
    ) -> WorkflowInstance:
        """
        Start a new workflow instance

        Args:
            workflow_key: Key of workflow definition
            business_key: Business identifier (e.g., case_id)
            variables: Initial workflow variables

        Returns:
            New WorkflowInstance
        """
        if workflow_key not in self.definitions:
            raise ValueError(f"Workflow {workflow_key} not found")

        definition = self.definitions[workflow_key]

        if not definition.enabled:
            raise ValueError(f"Workflow {workflow_key} is disabled")

        # Create instance
        instance = WorkflowInstance(
            id=str(uuid.uuid4()),
            workflow_key=workflow_key,
            status=WorkflowStatus.RUNNING,
            business_key=business_key,
            variables=variables or {}
        )

        # Create tasks from definition
        for task_def in definition.tasks:
            task = WorkflowTask(
                id=str(uuid.uuid4()),
                name=task_def["name"],
                task_type=task_def["type"],
                assignee=task_def.get("assignee"),
                due_date=self._calculate_due_date(task_def.get("due_in_days", 1)),
                handler=self.task_handlers.get(task_def["type"])
            )
            instance.tasks.append(task)

        # Activate first task
        if instance.tasks:
            instance.tasks[0].status = TaskStatus.ACTIVE
            instance.current_task = instance.tasks[0].id

        self.instances[instance.id] = instance

        logger.info(
            f"Workflow started: {workflow_key} for {business_key}, "
            f"instance_id={instance.id}"
        )

        return instance

    def complete_task(
        self,
        instance_id: str,
        task_id: str,
        variables: Dict[str, Any] = None
    ):
        """
        Complete a workflow task

        Args:
            instance_id: Workflow instance ID
            task_id: Task ID
            variables: Task output variables
        """
        instance = self.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        task = next((t for t in instance.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status != TaskStatus.ACTIVE:
            raise ValueError(f"Task {task_id} is not active")

        # Complete task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()

        # Merge variables
        if variables:
            instance.variables.update(variables)

        logger.info(f"Task completed: {task.name} in instance {instance_id}")

        # Activate next task
        self._activate_next_task(instance)

    def fail_task(self, instance_id: str, task_id: str, error: str):
        """Mark a task as failed"""
        instance = self.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        task = next((t for t in instance.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.FAILED
        instance.status = WorkflowStatus.FAILED
        instance.error = error

        logger.error(f"Task failed: {task.name}, error: {error}")

    def get_active_tasks(self, instance_id: str) -> List[WorkflowTask]:
        """Get all active tasks for an instance"""
        instance = self.instances.get(instance_id)
        if not instance:
            return []

        return [t for t in instance.tasks if t.status == TaskStatus.ACTIVE]

    def get_user_tasks(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a user"""
        tasks = []

        for instance in self.instances.values():
            if instance.status != WorkflowStatus.RUNNING:
                continue

            for task in instance.tasks:
                if (task.status == TaskStatus.ACTIVE and
                    task.assignee == assignee):
                    tasks.append({
                        "instance_id": instance.id,
                        "task_id": task.id,
                        "task_name": task.name,
                        "business_key": instance.business_key,
                        "due_date": task.due_date,
                        "variables": instance.variables
                    })

        return tasks

    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID"""
        return self.instances.get(instance_id)

    def get_instances_by_business_key(self, business_key: str) -> List[WorkflowInstance]:
        """Get all workflow instances for a business key"""
        return [
            inst for inst in self.instances.values()
            if inst.business_key == business_key
        ]

    def cancel_instance(self, instance_id: str):
        """Cancel a running workflow instance"""
        instance = self.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        instance.status = WorkflowStatus.CANCELLED

        # Cancel all active tasks
        for task in instance.tasks:
            if task.status == TaskStatus.ACTIVE:
                task.status = TaskStatus.CANCELLED

        logger.info(f"Workflow cancelled: {instance_id}")

    def _activate_next_task(self, instance: WorkflowInstance):
        """Activate the next task in the workflow"""
        current_index = next(
            (i for i, t in enumerate(instance.tasks) if t.id == instance.current_task),
            -1
        )

        if current_index < len(instance.tasks) - 1:
            # Activate next task
            next_task = instance.tasks[current_index + 1]
            next_task.status = TaskStatus.ACTIVE
            instance.current_task = next_task.id

            logger.info(f"Next task activated: {next_task.name}")

            # Auto-execute service tasks
            if next_task.task_type == "service_task" and next_task.handler:
                try:
                    result = next_task.handler(instance.variables)
                    self.complete_task(instance.id, next_task.id, result)
                except Exception as e:
                    self.fail_task(instance.id, next_task.id, str(e))
        else:
            # Workflow complete
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.now()
            instance.current_task = None

            logger.info(f"Workflow completed: {instance.id}")

    def _calculate_due_date(self, days: int) -> datetime:
        """Calculate task due date"""
        return datetime.now() + timedelta(days=days)

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow engine statistics"""
        total = len(self.instances)
        running = sum(1 for i in self.instances.values() if i.status == WorkflowStatus.RUNNING)
        completed = sum(1 for i in self.instances.values() if i.status == WorkflowStatus.COMPLETED)
        failed = sum(1 for i in self.instances.values() if i.status == WorkflowStatus.FAILED)

        return {
            "total_instances": total,
            "running": running,
            "completed": completed,
            "failed": failed,
            "registered_workflows": len(self.definitions),
            "registered_handlers": len(self.task_handlers)
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()
