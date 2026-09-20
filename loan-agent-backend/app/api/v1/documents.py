"""
Document Generation API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.documents.generator import document_generator

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


class GenerateLetterRequest(BaseModel):
    """Request to generate collection letter"""
    case_id: str
    letter_type: str = "initial"  # initial, reminder, final


class GeneratePaymentPlanRequest(BaseModel):
    """Request to generate payment plan"""
    case_id: str
    total_amount: float
    down_payment: float
    num_payments: int
    start_date: Optional[str] = None


class GenerateDemandLetterRequest(BaseModel):
    """Request to generate demand letter"""
    case_id: str
    deadline_days: int = 10


class GenerateSettlementRequest(BaseModel):
    """Request to generate settlement offer"""
    case_id: str
    settlement_amount: float


class GenerateReceiptRequest(BaseModel):
    """Request to generate payment receipt"""
    case_id: str
    payment_amount: float
    payment_method: str
    transaction_id: str


@router.post("/collection-letter")
async def generate_collection_letter(
    request: GenerateLetterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a collection letter

    Types:
    - **initial**: First contact letter
    - **reminder**: Follow-up reminder
    - **final**: Final notice before legal action
    """
    # Get case data (simplified)
    case_data = {
        "case_id": request.case_id,
        "loan_id": f"LOAN{request.case_id[-6:]}",
        "principal_amount": 50000.00,
        "overdue_amount": 5000.00,
        "overdue_days": 45
    }

    customer_data = {
        "name": "John Doe",
        "address": "123 Main Street, Anytown, ST 12345"
    }

    # Generate document
    content = document_generator.generate_collection_letter(
        case_data=case_data,
        customer_data=customer_data,
        letter_type=request.letter_type
    )

    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=collection_letter_{request.case_id}.html"}
    )


@router.post("/payment-plan")
async def generate_payment_plan(
    request: GeneratePaymentPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a payment plan agreement

    Creates a structured payment plan document with schedule
    """
    case_data = {
        "case_id": request.case_id,
        "loan_id": f"LOAN{request.case_id[-6:]}",
        "principal_amount": request.total_amount,
    }

    customer_data = {
        "name": "John Doe",
        "address": "123 Main Street, Anytown, ST 12345"
    }

    plan_details = {
        "total_amount": request.total_amount,
        "down_payment": request.down_payment,
        "num_payments": request.num_payments,
        "start_date": datetime.fromisoformat(request.start_date) if request.start_date else datetime.now()
    }

    content = document_generator.generate_payment_plan(
        case_data=case_data,
        customer_data=customer_data,
        plan_details=plan_details
    )

    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=payment_plan_{request.case_id}.html"}
    )


@router.post("/demand-letter")
async def generate_demand_letter(
    request: GenerateDemandLetterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a formal demand letter

    Final notice before legal action
    """
    case_data = {
        "case_id": request.case_id,
        "loan_id": f"LOAN{request.case_id[-6:]}",
        "overdue_amount": 5000.00,
        "overdue_days": 180
    }

    customer_data = {
        "name": "John Doe",
        "address": "123 Main Street, Anytown, ST 12345"
    }

    content = document_generator.generate_demand_letter(
        case_data=case_data,
        customer_data=customer_data,
        deadline_days=request.deadline_days
    )

    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=demand_letter_{request.case_id}.html"}
    )


@router.post("/settlement-offer")
async def generate_settlement_offer(
    request: GenerateSettlementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a settlement offer letter

    Offer to settle debt at reduced amount
    """
    original_amount = 10000.00  # Would fetch from case

    case_data = {
        "case_id": request.case_id,
        "loan_id": f"LOAN{request.case_id[-6:]}",
    }

    customer_data = {
        "name": "John Doe",
        "address": "123 Main Street, Anytown, ST 12345"
    }

    content = document_generator.generate_settlement_offer(
        case_data=case_data,
        customer_data=customer_data,
        settlement_amount=request.settlement_amount,
        original_amount=original_amount,
        expiry_days=30
    )

    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=settlement_offer_{request.case_id}.html"}
    )


@router.post("/receipt")
async def generate_receipt(
    request: GenerateReceiptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a payment receipt

    Official receipt for customer payment
    """
    case_data = {
        "case_id": request.case_id,
    }

    customer_data = {
        "name": "John Doe",
        "address": "123 Main Street, Anytown, ST 12345"
    }

    payment_data = {
        "receipt_number": f"RCP{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "amount": request.payment_amount,
        "method": request.payment_method,
        "transaction_id": request.transaction_id,
        "remaining_balance": 0.00  # Would calculate from case
    }

    content = document_generator.generate_receipt(
        case_data=case_data,
        customer_data=customer_data,
        payment_data=payment_data
    )

    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=receipt_{request.transaction_id}.html"}
    )


@router.get("/templates")
async def list_templates(
    current_user: Dict = Depends(get_current_user)
):
    """
    List all available document templates

    Returns information about available document types
    """
    return {
        "templates": [
            {
                "id": "collection_letter",
                "name": "Collection Letter",
                "types": ["initial", "reminder", "final"],
                "description": "Standard collection correspondence"
            },
            {
                "id": "payment_plan",
                "name": "Payment Plan Agreement",
                "description": "Structured payment arrangement"
            },
            {
                "id": "demand_letter",
                "name": "Demand Letter",
                "description": "Final notice before legal action"
            },
            {
                "id": "settlement_offer",
                "name": "Settlement Offer",
                "description": "Reduced amount settlement proposal"
            },
            {
                "id": "receipt",
                "name": "Payment Receipt",
                "description": "Official payment confirmation"
            },
            {
                "id": "cease_and_desist_ack",
                "name": "Cease & Desist Acknowledgment",
                "description": "FDCPA compliance acknowledgment"
            }
        ]
    }
