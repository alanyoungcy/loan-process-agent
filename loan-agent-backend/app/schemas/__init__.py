from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "collector"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Case Schemas
class CaseBase(BaseModel):
    customer_id: str
    loan_id: str
    loan_product: Optional[str] = None
    principal_amount: Optional[float] = None
    overdue_amount: Optional[float] = None
    overdue_days: Optional[int] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = None
    assigned_to: Optional[UUID] = None
    payment_promise: Optional[dict] = None
    tags: Optional[List[str]] = None


class CaseResponse(CaseBase):
    id: UUID
    case_id: str
    status: str
    priority: int
    assigned_to: Optional[UUID] = None
    contact_count: int
    last_contact_date: Optional[datetime] = None
    dispute_flag: bool
    legal_status: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Contact History Schemas
class ContactHistoryBase(BaseModel):
    case_id: UUID
    contact_type: str
    contact_time: datetime
    transcript: Optional[str] = None
    outcome: Optional[str] = None


class ContactHistoryCreate(ContactHistoryBase):
    pass


class ContactHistoryResponse(ContactHistoryBase):
    id: UUID
    contact_id: str
    duration_seconds: Optional[int] = None
    sentiment: Optional[str] = None
    intent: Optional[str] = None
    genai_processed: bool
    compliance_checked: bool
    compliance_violations: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Rule Schemas
class RuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str
    drl_content: Optional[str] = None
    priority: int = 5


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    drl_content: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class RuleResponse(RuleBase):
    id: UUID
    rule_id: str
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# GenAI Schemas
class GenAISummarizeRequest(BaseModel):
    case_id: UUID


class GenAISummarizeResponse(BaseModel):
    summary: str
    confidence: float
    processing_time_ms: int


class GenAIScriptGenerateRequest(BaseModel):
    case_id: UUID
    scenario: str
    tone: str = "professional"


class GenAIScriptGenerateResponse(BaseModel):
    script: str
    confidence: float
    compliance_checked: bool
    compliance_issues: Optional[List[str]] = None


class GenAIIntentAnalysisRequest(BaseModel):
    transcript: str


class GenAIIntentAnalysisResponse(BaseModel):
    intent: str
    sentiment: str
    confidence: float
    key_phrases: List[str]


# Task Queue Schemas
class TaskCreate(BaseModel):
    task_type: str
    payload: dict
    priority: int = 5


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analytics Schemas
class PerformanceMetrics(BaseModel):
    total_cases: int
    active_cases: int
    resolved_cases: int
    avg_resolution_time_days: float
    contact_success_rate: float
    compliance_rate: float
    recovery_rate: float


class ComplianceMetrics(BaseModel):
    total_violations: int
    violations_by_type: dict
    violations_by_severity: dict
    resolution_rate: float
    avg_resolution_time_hours: float
