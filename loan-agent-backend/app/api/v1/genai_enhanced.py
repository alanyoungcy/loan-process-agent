"""
Enhanced GenAI API endpoints with Trust Gate and Async Task Support
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import time
import json

from app.db.session import get_db
from app.models.case import Case, GenAIAudit
from app.models.additional import GenAIReviewQueue, ContactHistory
from app.schemas import (
    GenAISummarizeRequest,
    GenAISummarizeResponse,
    GenAIScriptGenerateRequest,
    GenAIScriptGenerateResponse,
    GenAIIntentAnalysisRequest,
    GenAIIntentAnalysisResponse,
)
from app.core.security import get_current_user
from app.services.genai.summarizer import SummarizerService
from app.services.genai.script_generator import ScriptGenerator
from app.services.genai.intent_analyzer import IntentAnalyzer
from app.services.genai.willingness_scorer import WillingnessScorer
from app.services.trust_gate import get_trust_gate
from app.services.mq.rabbitmq_client import get_mq_client
from sqlalchemy import select
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()


# ✅ ENHANCED: Summarize with Trust Gate
@router.post("/summarize", response_model=GenAISummarizeResponse)
async def summarize_case(
    request: GenAISummarizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI summary for a case with Trust Gate evaluation"""
    start_time = time.time()

    # Get case
    result = await db.execute(
        select(Case).where(Case.id == request.case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    try:
        # Generate summary
        summarizer = SummarizerService()
        result = await summarizer.summarize(case)

        processing_time = int((time.time() - start_time) * 1000)

        # ✅ Trust Gate evaluation
        trust_gate = get_trust_gate()
        evaluation = trust_gate.evaluate(
            genai_output=result,
            context={
                "overdue_amount": float(case.overdue_amount),
                "overdue_days": case.overdue_days,
                "customer_segment": "standard",
                "priority": case.priority
            }
        )

        # ✅ Route based on Trust Gate decision
        if evaluation["requires_review"]:
            # Create review queue entry
            review_entry = GenAIReviewQueue(
                case_id=case.id,
                service_type="summarize",
                genai_output=result,
                trust_gate_evaluation=evaluation,
                priority=trust_gate.calculate_review_priority(evaluation)
            )
            db.add(review_entry)

        # Log to audit
        audit = GenAIAudit(
            case_id=case.id,
            service_type="summarize",
            model_used="gpt-4",
            confidence=result["confidence"],
            processing_time_ms=processing_time,
            user_id=current_user.get("id")
        )
        db.add(audit)
        await db.commit()

        return GenAISummarizeResponse(
            summary=result["summary"],
            confidence=result["confidence"],
            processing_time_ms=processing_time,
            trust_gate_decision=evaluation["decision"],
            requires_review=evaluation["requires_review"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


# ✅ NEW: Async summarize endpoint
@router.post("/summarize/async")
async def summarize_case_async(
    request: GenAISummarizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit async summarization task"""

    # Verify case exists
    result = await db.execute(
        select(Case).where(Case.id == request.case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    try:
        # Publish to message queue
        mq_client = await get_mq_client()
        task_id = await mq_client.publish_task(
            queue_name="genai.summarize",
            task_data={"case_id": str(request.case_id)},
            priority=5
        )

        # Store task status in Redis
        redis_client = await redis.from_url(settings.REDIS_URL)
        await redis_client.setex(
            f"task:{task_id}:status",
            3600,  # 1 hour TTL
            "pending"
        )
        await redis_client.close()

        return {
            "task_id": task_id,
            "status": "pending",
            "status_url": f"/api/v1/genai/tasks/{task_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task: {str(e)}"
        )


# ✅ ENHANCED: Generate script with Trust Gate
@router.post("/generate-script", response_model=GenAIScriptGenerateResponse)
async def generate_script(
    request: GenAIScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate collection script using AI with Trust Gate evaluation"""
    start_time = time.time()

    # Get case
    result = await db.execute(
        select(Case).where(Case.id == request.case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    try:
        # Generate script with RAG
        generator = ScriptGenerator()
        result = await generator.generate_script(
            case=case,
            scenario=request.scenario,
            tone=request.tone
        )

        processing_time = int((time.time() - start_time) * 1000)

        # ✅ Trust Gate evaluation
        trust_gate = get_trust_gate()
        evaluation = trust_gate.evaluate(
            genai_output=result,
            context={
                "overdue_amount": float(case.overdue_amount),
                "overdue_days": case.overdue_days,
                "customer_segment": "standard",
                "priority": case.priority,
                "dispute_flag": case.dispute_flag,
                "legal_flag": case.legal_flag
            }
        )

        # ✅ Route based on Trust Gate decision
        if evaluation["requires_review"]:
            review_entry = GenAIReviewQueue(
                case_id=case.id,
                service_type="generate_script",
                genai_output=result,
                trust_gate_evaluation=evaluation,
                priority=trust_gate.calculate_review_priority(evaluation)
            )
            db.add(review_entry)

        # Log to audit
        audit = GenAIAudit(
            case_id=case.id,
            service_type="script_generation",
            model_used="gpt-4",
            confidence=result["confidence"],
            processing_time_ms=processing_time,
            user_id=current_user.get("id")
        )
        db.add(audit)
        await db.commit()

        return GenAIScriptGenerateResponse(
            script=result["script"],
            confidence=result["confidence"],
            compliance_checked=result["compliance_checked"],
            compliance_issues=result["compliance_issues"],
            trust_gate_decision=evaluation["decision"],
            requires_review=evaluation["requires_review"],
            risk_level=evaluation["risk_level"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate script: {str(e)}"
        )


# ✅ NEW: Async script generation
@router.post("/generate-script/async")
async def generate_script_async(
    request: GenAIScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit async script generation task"""

    # Verify case exists
    result = await db.execute(
        select(Case).where(Case.id == request.case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    try:
        # Get case data
        case_data = {
            "customer_id": case.customer_id,
            "overdue_amount": float(case.overdue_amount),
            "overdue_days": case.overdue_days,
            "status": case.status,
            "contact_count": case.contact_count
        }

        # Publish to message queue
        mq_client = await get_mq_client()
        task_id = await mq_client.publish_task(
            queue_name="genai.script_generation",
            task_data={
                "case_data": case_data,
                "scenario": request.scenario
            },
            priority=7  # Higher priority for scripts
        )

        # Store task status
        redis_client = await redis.from_url(settings.REDIS_URL)
        await redis_client.setex(f"task:{task_id}:status", 3600, "pending")
        await redis_client.close()

        return {
            "task_id": task_id,
            "status": "pending",
            "status_url": f"/api/v1/genai/tasks/{task_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task: {str(e)}"
        )


# ✅ NEW: Task status endpoint
@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check status of async task"""

    try:
        redis_client = await redis.from_url(settings.REDIS_URL)

        status_key = f"task:{task_id}:status"
        result_key = f"task:{task_id}:result"

        status = await redis_client.get(status_key)

        if not status:
            await redis_client.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        response = {
            "task_id": task_id,
            "status": status
        }

        if status == "completed":
            result = await redis_client.get(result_key)
            if result:
                response["result"] = json.loads(result) if isinstance(result, str) else result
        elif status == "failed":
            result = await redis_client.get(result_key)
            if result:
                response["error"] = result

        await redis_client.close()
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


# ✅ NEW: Batch summarization
@router.post("/batch/summarize")
async def batch_summarize(
    case_ids: list[UUID],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit batch summarization task"""

    if len(case_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 cases per batch"
        )

    try:
        # Publish to batch queue
        mq_client = await get_mq_client()
        task_id = await mq_client.publish_task(
            queue_name="genai.batch_processing",
            task_data={"case_ids": [str(cid) for cid in case_ids]},
            priority=3
        )

        redis_client = await redis.from_url(settings.REDIS_URL)
        await redis_client.setex(f"task:{task_id}:status", 7200, "pending")  # 2 hour TTL
        await redis_client.close()

        return {
            "task_id": task_id,
            "status": "pending",
            "case_count": len(case_ids),
            "status_url": f"/api/v1/genai/tasks/{task_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit batch task: {str(e)}"
        )


# Existing endpoints (kept for compatibility)
@router.post("/analyze-intent", response_model=GenAIIntentAnalysisResponse)
async def analyze_intent(
    request: GenAIIntentAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze customer intent and sentiment from transcript"""
    start_time = time.time()

    try:
        analyzer = IntentAnalyzer()
        result = await analyzer.analyze(request.transcript)

        processing_time = int((time.time() - start_time) * 1000)

        audit = GenAIAudit(
            case_id=None,
            service_type="intent_analysis",
            model_used="gpt-4",
            confidence=result["confidence"],
            processing_time_ms=processing_time,
            user_id=current_user.get("id")
        )
        db.add(audit)
        await db.commit()

        return GenAIIntentAnalysisResponse(
            intent=result["intent"],
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            key_phrases=result["key_phrases"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze intent: {str(e)}"
        )


@router.post("/score-willingness")
async def score_willingness(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Score customer's willingness to pay using AI"""
    start_time = time.time()

    result = await db.execute(
        select(Case).where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    # Get contact history
    contact_result = await db.execute(
        select(ContactHistory)
        .where(ContactHistory.case_id == case_id)
        .order_by(ContactHistory.contact_time.desc())
        .limit(10)
    )
    contact_history = contact_result.scalars().all()

    try:
        scorer = WillingnessScorer()
        result = await scorer.score(case, contact_history)

        processing_time = int((time.time() - start_time) * 1000)

        audit = GenAIAudit(
            case_id=case.id,
            service_type="willingness_scoring",
            model_used="gpt-4",
            confidence=result["confidence"],
            processing_time_ms=processing_time,
            user_id=current_user.get("id")
        )
        db.add(audit)
        await db.commit()

        return {
            "case_id": str(case_id),
            "willingness_score": result["willingness_score"],
            "factors": result["factors"],
            "confidence": result["confidence"],
            "recommendation": result["recommendation"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score willingness: {str(e)}"
        )
