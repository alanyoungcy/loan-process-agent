from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models import Case, Customer
from app.schemas import CaseResponse, CaseCreate, CaseUpdate
from app.core.security import get_current_user
import uuid

router = APIRouter()


@router.get("/", response_model=List[CaseResponse])
async def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of cases with pagination and filters"""
    query = select(Case)

    # Apply filters
    if status:
        query = query.where(Case.status == status)
    if assigned_to:
        query = query.where(Case.assigned_to == assigned_to)

    # Order by priority and creation date
    query = query.order_by(desc(Case.priority), desc(Case.created_at))
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    cases = result.scalars().all()

    return cases


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get case by ID"""
    result = await db.execute(
        select(Case).where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    return case


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new case"""
    # Generate unique case ID
    case_id = f"CASE{uuid.uuid4().hex[:8].upper()}"

    new_case = Case(
        case_id=case_id,
        customer_id=case_data.customer_id,
        loan_id=case_data.loan_id,
        loan_product=case_data.loan_product,
        principal_amount=case_data.principal_amount,
        overdue_amount=case_data.overdue_amount,
        overdue_days=case_data.overdue_days,
        status="new",
        priority=5
    )

    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    return new_case


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    case_update: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update case"""
    result = await db.execute(
        select(Case).where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    # Update fields
    update_data = case_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)

    return case


@router.post("/{case_id}/assign")
async def assign_case(
    case_id: UUID,
    assigned_to: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Assign case to collector"""
    result = await db.execute(
        select(Case).where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    case.assigned_to = assigned_to
    case.status = "assigned"

    await db.commit()
    await db.refresh(case)

    return {"message": "Case assigned successfully", "case_id": str(case.id)}


@router.get("/{case_id}/timeline")
async def get_case_timeline(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get case timeline with all contacts and events"""
    # This is a placeholder - will be implemented with contact history
    result = await db.execute(
        select(Case).where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    return {
        "case_id": str(case.id),
        "events": [],
        "contacts": []
    }


@router.get("/stats/summary")
async def get_case_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get case statistics summary"""
    # Total cases
    total_result = await db.execute(select(func.count(Case.id)))
    total_cases = total_result.scalar()

    # Active cases
    active_result = await db.execute(
        select(func.count(Case.id)).where(Case.status.in_(["new", "in_progress", "assigned"]))
    )
    active_cases = active_result.scalar()

    # Resolved cases
    resolved_result = await db.execute(
        select(func.count(Case.id)).where(Case.status == "resolved")
    )
    resolved_cases = resolved_result.scalar()

    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "resolved_cases": resolved_cases,
        "resolution_rate": round(resolved_cases / total_cases * 100, 2) if total_cases > 0 else 0
    }
