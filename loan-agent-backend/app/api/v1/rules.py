"""
Rules Engine API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.camunda_dmn.rules_service import rules_service
from app.models import Case

router = APIRouter(tags=["Rules Engine"])


class EvaluateRequest(BaseModel):
    """Request to evaluate a case against rules"""
    case_id: str
    additional_facts: Dict[str, Any] = {}
    auto_apply: bool = False


class EvaluateResponse(BaseModel):
    """Response from rule evaluation"""
    case_id: str
    rules_executed: List[str]
    actions_taken: List[str]
    modifications: Dict[str, Any]
    recommendations: List[str]
    can_contact: bool
    applied: bool


class RuleInfo(BaseModel):
    """Information about a rule"""
    name: str
    description: str
    priority: str
    enabled: bool
    tags: List[str]


class RulesStatistics(BaseModel):
    """Rules engine statistics"""
    total_rules: int
    enabled_rules: int
    total_executions: int
    successful_executions: int
    failed_executions: int


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_case(
    request: EvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Evaluate a case against business rules

    Runs all applicable business rules against the specified case
    and returns recommendations and suggested modifications.

    - **case_id**: Case ID to evaluate
    - **additional_facts**: Optional additional context
    - **auto_apply**: Whether to automatically apply modifications
    """
    # Get case
    result = await db.execute(
        f"SELECT * FROM cases WHERE id = '{request.case_id}' LIMIT 1"
    )
    case = result.first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {request.case_id} not found"
        )

    # Convert to Case object (simplified - in production use proper ORM)
    case_obj = Case(
        id=case.id,
        case_id=case.case_id,
        customer_id=case.customer_id,
        loan_id=case.loan_id,
        loan_product=case.loan_product,
        principal_amount=case.principal_amount,
        overdue_amount=case.overdue_amount,
        overdue_days=case.overdue_days,
        status=case.status,
        priority=case.priority,
        contact_count=case.contact_count,
        dispute_flag=case.dispute_flag,
        legal_flag=case.legal_flag,
    )

    # Evaluate rules
    evaluation = await rules_service.apply_rules_to_case(
        case=case_obj,
        db=db,
        additional_facts=request.additional_facts,
        auto_apply=request.auto_apply
    )

    return EvaluateResponse(
        case_id=request.case_id,
        rules_executed=evaluation["rules_executed"],
        actions_taken=evaluation["actions_taken"],
        modifications=evaluation["modifications"],
        recommendations=evaluation["recommendations"],
        can_contact=evaluation["can_contact"],
        applied=evaluation.get("applied", False)
    )


@router.get("/list", response_model=List[RuleInfo])
async def list_rules(
    category: str = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    List all registered business rules

    Returns information about all rules in the system.
    Optionally filter by category tag.

    - **category**: Optional category filter (e.g., 'compliance', 'priority')
    """
    if category:
        rule_names = rules_service.get_rules_by_category(category)
        all_rules = rules_service.get_all_rules()
        return [r for r in all_rules if r["name"] in rule_names]
    else:
        return rules_service.get_all_rules()


@router.get("/statistics", response_model=RulesStatistics)
async def get_statistics(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get rules engine execution statistics

    Returns statistics about rule execution, including:
    - Total number of rules
    - Number of enabled rules
    - Execution counts
    """
    stats = rules_service.get_statistics()
    return RulesStatistics(**stats)


@router.post("/enable/{rule_name}")
async def enable_rule(
    rule_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Enable a specific rule

    - **rule_name**: Name of the rule to enable
    """
    # Allow all authenticated users to enable/disable rules
    rules_service.enable_rule(rule_name)
    return {"message": f"Rule '{rule_name}' enabled"}


@router.post("/disable/{rule_name}")
async def disable_rule(
    rule_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Disable a specific rule

    - **rule_name**: Name of the rule to disable
    """
    # Allow all authenticated users to enable/disable rules
    rules_service.disable_rule(rule_name)
    return {"message": f"Rule '{rule_name}' disabled"}


@router.get("/categories")
async def get_categories(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all rule categories

    Returns a list of all unique rule categories/tags
    """
    all_rules = rules_service.get_all_rules()
    categories = set()
    for rule in all_rules:
        categories.update(rule["tags"])

    return {"categories": sorted(list(categories))}
