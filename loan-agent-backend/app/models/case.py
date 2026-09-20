"""
Case Model - Core business entity for loan collection cases
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import Base


class Case(Base):
    """
    Loan Collection Case Model

    Represents a single loan collection case with customer and loan information
    """
    __tablename__ = "cases"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(50), unique=True, nullable=False, index=True)

    # Customer and Loan references
    customer_id = Column(String(50), nullable=False, index=True)
    loan_id = Column(String(50), nullable=False, index=True)
    loan_product = Column(String(100))

    # Financial information
    principal_amount = Column(Numeric(15, 2), nullable=False)
    overdue_amount = Column(Numeric(15, 2), nullable=False)
    overdue_days = Column(Integer, nullable=False, default=0)
    overdue_date = Column(DateTime, nullable=True)

    # Case status and priority
    status = Column(String(50), nullable=False, default="new", index=True)
    # Status values: new, in_progress, contacted, promised_to_pay, payment_plan,
    #                dispute, legal, closed, written_off

    priority = Column(Integer, nullable=False, default=5)  # 1-10 scale

    # Contact tracking
    contact_count = Column(Integer, default=0)
    last_contact_date = Column(DateTime, nullable=True)
    next_action_date = Column(DateTime, nullable=True)

    # Assignment
    assigned_to = Column(String(50), nullable=True, index=True)

    # Flags
    dispute_flag = Column(Boolean, default=False)
    legal_flag = Column(Boolean, default=False)

    # Additional data
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Case {self.case_id} - {self.status}>"


class Customer(Base):
    """
    Customer Model

    Stores customer information for loan collection
    """
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)

    # Personal information
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(200))
    id_number = Column(String(50))

    # Address
    address = Column(String(500))

    # Risk information
    credit_score = Column(Integer)
    risk_category = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Customer {self.customer_id} - {self.name}>"


class GenAIAudit(Base):
    """
    GenAI Audit Log

    Tracks all GenAI API calls for audit and cost tracking
    """
    __tablename__ = "genai_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Request information
    case_id = Column(UUID(as_uuid=True), nullable=True)
    service_type = Column(String(50), nullable=False)  # summarize, generate_script, etc.

    # LLM details
    model_used = Column(String(100))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Performance
    confidence = Column(Numeric(3, 2), nullable=True)
    processing_time_ms = Column(Integer)

    # User tracking
    user_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<GenAIAudit {self.service_type} - {self.total_tokens} tokens>"


class CollectionActivity(Base):
    """
    Collection Activity Log

    Tracks all collection activities and interactions
    """
    __tablename__ = "collection_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Case reference
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Activity details
    activity_type = Column(String(50), nullable=False)
    # Types: call, email, sms, letter, payment, promise, dispute, note

    activity_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Content
    summary = Column(String(500))
    details = Column(Text)

    # Outcome
    outcome = Column(String(100))
    next_action = Column(String(500))

    # User tracking
    performed_by = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Activity {self.activity_type} on {self.activity_date}>"


class Payment(Base):
    """
    Payment Model

    Tracks payments received for cases
    """
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Case reference
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Payment details
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # cash, check, card, bank_transfer, etc.

    # Transaction details
    transaction_id = Column(String(100), unique=True)
    reference_number = Column(String(100))

    # Status
    status = Column(String(50), default="completed")
    # Status values: pending, completed, failed, reversed

    # Notes
    notes = Column(Text)

    # User tracking
    received_by = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Payment ${self.amount} on {self.payment_date}>"
