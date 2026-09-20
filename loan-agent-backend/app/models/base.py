from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ARRAY, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), nullable=False, default="collector")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_cases = relationship("Case", back_populates="assigned_user")
    contact_history = relationship("ContactHistory", back_populates="creator")


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    id_card = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    employment_status = Column(String(30))
    monthly_income = Column(Float)
    credit_score = Column(Integer)
    customer_segment = Column(String(20))
    registration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Case(Base):
    """Collection case model"""
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    loan_id = Column(String(50), nullable=False)
    loan_product = Column(String(50))
    principal_amount = Column(Float)
    overdue_amount = Column(Float)
    overdue_days = Column(Integer, index=True)
    overdue_date = Column(DateTime)
    status = Column(String(30), default="new", index=True)
    priority = Column(Integer, default=5)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    contact_count = Column(Integer, default=0)
    last_contact_date = Column(DateTime)
    payment_promise = Column(JSON)
    dispute_flag = Column(Boolean, default=False)
    legal_status = Column(String(30))
    tags = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = relationship("User", back_populates="assigned_cases")
    contact_history = relationship("ContactHistory", back_populates="case", cascade="all, delete-orphan")
    compliance_violations = relationship("ComplianceViolation", back_populates="case")
    workflow_instances = relationship("WorkflowInstance", back_populates="case", cascade="all, delete-orphan")


class ContactHistory(Base):
    """Contact history model"""
    __tablename__ = "contact_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String(50), unique=True, nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    contact_type = Column(String(20), nullable=False)
    contact_time = Column(DateTime, nullable=False, index=True)
    duration_seconds = Column(Integer)
    transcript = Column(Text)
    sentiment = Column(String(20))
    intent = Column(String(50))
    outcome = Column(String(50))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    genai_processed = Column(Boolean, default=False)
    compliance_checked = Column(Boolean, default=False)
    compliance_violations = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="contact_history")
    creator = relationship("User", back_populates="contact_history")


class Rule(Base):
    """Rule model"""
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    rule_type = Column(String(30), nullable=False, index=True)
    drl_content = Column(Text)
    decision_table_path = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=5)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenAIAudit(Base):
    """GenAI audit log model"""
    __tablename__ = "genai_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    service_type = Column(String(50), nullable=False, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence = Column(Float)
    trust_gate_decision = Column(String(20))
    human_review_result = Column(String(20))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ScriptTemplate(Base):
    """Script template model"""
    __tablename__ = "script_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    scenario = Column(String(50))
    content = Column(Text, nullable=False)
    compliance_validated = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)
    tags = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceViolation(Base):
    """Compliance violation model"""
    __tablename__ = "compliance_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact_history.id"))
    violation_type = Column(String(50), nullable=False)
    description = Column(Text)
    severity = Column(String(20))
    detected_by = Column(String(20))
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    case = relationship("Case", back_populates="compliance_violations")


class TaskQueue(Base):
    """Task queue model for async jobs"""
    __tablename__ = "task_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(50), unique=True, nullable=False, index=True)
    task_type = Column(String(50), nullable=False, index=True)
    payload = Column(JSON)
    status = Column(String(20), default="pending", index=True)
    result = Column(JSON)
    error = Column(Text)
    priority = Column(Integer, default=5)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
