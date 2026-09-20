"""
Additional Models for Complete System
Includes: Rules, ScriptTemplates, ComplianceViolations, ABTesting, ReviewQueue
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import Base


class Rule(Base):
    """
    Rule Model for Dynamic Rule Management
    """
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    rule_type = Column(String(30), nullable=False, index=True)
    # Types: compliance, assignment, strategy, priority, risk

    # Rule content
    drl_content = Column(Text)
    decision_table_path = Column(String(255))

    # Status and versioning
    is_active = Column(Boolean, default=True, index=True)
    version = Column(Integer, default=1)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50))
    updated_by = Column(String(50))

    # Performance tracking
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime)

    def __repr__(self):
        return f"<Rule {self.name} - {self.rule_type}>"


class ScriptTemplate(Base):
    """
    Script Template Model
    Stores approved collection scripts with effectiveness tracking
    """
    __tablename__ = "script_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    scenario = Column(String(50), nullable=False, index=True)
    # Scenarios: first_contact, payment_reminder, payment_plan, dispute, final_notice, etc.

    content = Column(Text, nullable=False)
    language = Column(String(10), default="en")  # en, zh-HK, etc.

    # Compliance and effectiveness
    compliance_validated = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)  # 0.0-1.0
    success_rate = Column(Float)  # Conversion rate

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50))

    # Tags for searching
    tags = Column(JSON)

    def __repr__(self):
        return f"<ScriptTemplate {self.name} - {self.scenario}>"


class ComplianceViolation(Base):
    """
    Compliance Violation Model
    Tracks detected compliance violations
    """
    __tablename__ = "compliance_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    case_id = Column(UUID(as_uuid=True), index=True)
    contact_id = Column(UUID(as_uuid=True), index=True)
    activity_id = Column(UUID(as_uuid=True), index=True)

    # Violation details
    violation_type = Column(String(50), nullable=False, index=True)
    # Types: outside_contact_hours, excessive_frequency, threatening_language,
    #        third_party_disclosure, no_collector_identification, misrepresentation, etc.

    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical

    # Detection
    detected_by = Column(String(20), nullable=False)  # drools, genai, human
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Evidence
    evidence = Column(JSON)  # Transcript snippet, rule fired, etc.

    # Resolution
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(50))
    resolution_notes = Column(Text)

    # Actions taken
    action_taken = Column(String(100))  # warning, retraining, suspension, etc.

    def __repr__(self):
        return f"<ComplianceViolation {self.violation_type} - {self.severity}>"


class ABTestExperiment(Base):
    """
    A/B Test Experiment Model
    """
    __tablename__ = "ab_test_experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    # Experiment configuration
    control_description = Column(Text)
    treatment_description = Column(Text)
    hypothesis = Column(Text)

    # Timeline
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), default="active")  # active, completed, paused

    # Metrics
    target_metric = Column(String(50))  # payment_rate, contact_success, etc.
    target_sample_size = Column(Integer)

    # Results
    control_success_count = Column(Integer, default=0)
    control_total_count = Column(Integer, default=0)
    treatment_success_count = Column(Integer, default=0)
    treatment_total_count = Column(Integer, default=0)

    statistical_significance = Column(Float)  # p-value
    winner = Column(String(20))  # control, treatment, inconclusive

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50))

    def __repr__(self):
        return f"<ABTestExperiment {self.name} - {self.status}>"


class ABTestAssignment(Base):
    """
    A/B Test Assignment Model
    Tracks which cases are assigned to which variant
    """
    __tablename__ = "ab_test_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    experiment_name = Column(String(100), nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Assignment
    variant = Column(String(20), nullable=False)  # control, treatment
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Outcome
    outcome_data = Column(JSON)
    completed_at = Column(DateTime)
    success = Column(Boolean)

    def __repr__(self):
        return f"<ABTestAssignment {self.experiment_name} - {self.variant}>"


class GenAIReviewQueue(Base):
    """
    GenAI Review Queue Model
    Stores GenAI outputs requiring human review (Trust Gate routing)
    """
    __tablename__ = "genai_review_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    case_id = Column(UUID(as_uuid=True), index=True)
    service_type = Column(String(50), nullable=False)
    # Types: summarize, generate_script, analyze_intent, score_willingness, etc.

    # GenAI output
    genai_output = Column(JSON, nullable=False)
    trust_gate_evaluation = Column(JSON, nullable=False)

    # Review status
    status = Column(String(20), default="pending", index=True)
    # Status: pending, in_review, approved, rejected, escalated

    priority = Column(Integer, default=5)  # 1-10

    # Assignment
    assigned_reviewer = Column(UUID(as_uuid=True), index=True)
    assigned_at = Column(DateTime)

    # Review outcome
    reviewed_at = Column(DateTime)
    reviewer_decision = Column(JSON)
    reviewer_comments = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<GenAIReviewQueue {self.service_type} - {self.status}>"


class ContactHistory(Base):
    """
    Contact History Model
    Enhanced version with transcript analysis fields
    """
    __tablename__ = "contact_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Case reference
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Contact details
    contact_type = Column(String(20), nullable=False)  # call, sms, email, whatsapp
    contact_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = Column(Integer)

    # Content
    transcript = Column(Text)
    recording_url = Column(String(500))

    # GenAI analysis
    sentiment = Column(String(20))  # positive, neutral, negative
    intent = Column(String(50))  # willing_to_pay, dispute, need_time, etc.
    key_phrases = Column(JSON)

    # Outcome
    outcome = Column(String(50))
    # Outcomes: payment_promised, payment_arranged, dispute_raised, no_answer, etc.

    # Compliance
    compliance_checked = Column(Boolean, default=False)
    compliance_violations = Column(JSON)

    # User tracking
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ContactHistory {self.contact_type} - {self.outcome}>"
