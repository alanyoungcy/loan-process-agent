"""
Workflow Models - Database models for workflow instances and tasks
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base


class WorkflowInstance(Base):
    """
    Workflow Instance Model

    Represents a running or completed workflow instance linked to a case
    """
    __tablename__ = "workflow_instances"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Workflow definition reference
    workflow_key = Column(String(100), nullable=False, index=True)
    # Keys: standard_collection, payment_plan, dispute_resolution,
    #       legal_escalation, early_stage, settlement

    # Case reference
    case_id = Column(UUID(as_uuid=True), ForeignKey('cases.id'), nullable=False, index=True)

    # Business key (optional human-readable identifier)
    business_key = Column(String(100), index=True)

    # Status
    status = Column(String(20), nullable=False, default='running', index=True)
    # Status values: created, running, completed, failed, cancelled

    # Current state
    current_task_id = Column(String(100))
    current_task_name = Column(String(200))

    # Variables (workflow context data stored as JSON)
    variables = Column(JSONB, default={})

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Integration IDs (for external systems like Camunda)
    external_process_instance_id = Column(String(100), index=True)

    # Relationships
    case = relationship("Case", back_populates="workflow_instances")
    tasks = relationship("WorkflowTask", back_populates="workflow_instance", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowInstance {self.workflow_key} for Case {self.business_key}>"


class WorkflowTask(Base):
    """
    Workflow Task Model

    Represents an individual task within a workflow instance
    """
    __tablename__ = "workflow_tasks"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Workflow instance reference
    workflow_instance_id = Column(
        UUID(as_uuid=True),
        ForeignKey('workflow_instances.id'),
        nullable=False,
        index=True
    )

    # Task definition
    task_key = Column(String(100), nullable=False)
    task_name = Column(String(200), nullable=False)
    task_type = Column(String(50))  # user_task, service_task, script_task

    # Assignment
    assignee = Column(String(50), index=True)
    candidate_group = Column(String(50))

    # Status
    status = Column(String(20), nullable=False, default='pending', index=True)
    # Status values: pending, active, completed, failed, cancelled

    # Priority
    priority = Column(String(20), default='normal')
    # Priority values: low, normal, high, urgent

    # Due date
    due_date = Column(DateTime)

    # Task variables/form data
    variables = Column(JSONB, default={})

    # Result/outcome
    outcome = Column(String(100))
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Integration IDs (for external systems like Camunda)
    external_task_id = Column(String(100), index=True)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="tasks")

    def __repr__(self):
        return f"<WorkflowTask {self.task_name} - {self.status}>"
