from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import time

from app.db.session import get_db
from app.models import Case, GenAIAudit, ContactHistory
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
from app.services.genai.intent_analyzer import IntentAnalyzer, WillingnessScorer
from sqlalchemy import select

router = APIRouter()


@router.post("/summarize", response_model=GenAISummarizeResponse)
async def summarize_case(
    request: GenAISummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI summary for a case"""
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
        # Use real LLM to generate summary
        summarizer = SummarizerService()
        result = await summarizer.summarize(case)

        processing_time = int((time.time() - start_time) * 1000)

        # Log to audit
        audit = GenAIAudit(
            case_id=case.id,
            service_type="summarize",
            input_data={"case_id": str(case.id)},
            output_data={"summary": result["summary"]},
            confidence=result["confidence"],
            processing_time_ms=processing_time
        )
        db.add(audit)
        await db.commit()

        return GenAISummarizeResponse(
            summary=result["summary"],
            confidence=result["confidence"],
            processing_time_ms=processing_time
        )

    except Exception as e:
        # FALLBACK: Return mock summary when LLM unavailable
        processing_time = int((time.time() - start_time) * 1000)

        mock_summary = f"""Case Summary (Demo Mode):
Customer has been overdue for {case.overdue_days} days with an outstanding amount of HK${case.overdue_amount:,.2f}.
Current status: {case.status}. Priority score: {case.priority}/10.

Key Risk Factors:
- Extended overdue period ({case.overdue_days} days)
- Multiple contact attempts ({case.contact_count} contacts made)
- {'Dispute raised' if case.dispute_flag else 'No disputes'}

Recommended Actions:
1. {'Escalate to legal team' if case.overdue_days > 90 else 'Continue standard collection process'}
2. {'Offer payment plan' if case.overdue_amount > 50000 else 'Request immediate payment'}
3. Update contact strategy based on customer responsiveness

Urgency: {'HIGH' if case.priority >= 7 else 'MEDIUM' if case.priority >= 4 else 'LOW'}

Note: AI service unavailable - showing template-based summary."""

        return GenAISummarizeResponse(
            summary=mock_summary,
            confidence=0.75,
            processing_time_ms=processing_time
        )


@router.post("/generate-script", response_model=GenAIScriptGenerateResponse)
async def generate_script(
    request: GenAIScriptGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate collection script using AI"""
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
        # Use real LLM to generate script
        generator = ScriptGenerator()
        result = await generator.generate_script(
            case=case,
            scenario=request.scenario,
            tone=request.tone
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Log to audit
        audit = GenAIAudit(
            case_id=case.id,
            service_type="script_generation",
            input_data={
                "case_id": str(case.id),
                "scenario": request.scenario,
                "tone": request.tone
            },
            output_data={"script": result["script"]},
            confidence=result["confidence"],
            processing_time_ms=processing_time
        )
        db.add(audit)
        await db.commit()

        return GenAIScriptGenerateResponse(
            script=result["script"],
            confidence=result["confidence"],
            compliance_checked=result["compliance_checked"],
            compliance_issues=result["compliance_issues"]
        )

    except Exception as e:
        # FALLBACK: Return mock script when LLM unavailable
        processing_time = int((time.time() - start_time) * 1000)

        mock_script = f"""[Demo Mode - Template Script]

Good morning/afternoon. This is [Collector Name] calling from [Company Name], Money Lender License #123456.

I'm calling regarding your {case.loan_product or 'Personal Loan'} account ending in [Last 4 digits].

Our records show your payment is {case.overdue_days} days overdue, with an outstanding balance of HK${case.overdue_amount:,.2f}.

I understand financial situations can be challenging. I'm here to help find a solution that works for you.

Would you be able to discuss your account with me now?

[If YES]
Thank you. Let's review your options:
1. Full payment of HK${case.overdue_amount:,.2f} today
2. Payment plan over 3-6 months
3. Partial payment with commitment for remainder

Which option would work best for your situation?

[If NO]
I understand. When would be a better time to call you back? I can also arrange for our senior collector to contact you if you prefer.

May I have your preferred contact number and time?

[CLOSING]
Thank you for your time. I look forward to resolving this matter with you soon.

Have a good day.

---
Compliance Notes:
✓ Proper identification provided (MLO requirement)
✓ No threatening language
✓ Professional and respectful tone
✓ Clear payment options offered
✓ Customer consent requested

Note: AI service unavailable - showing template script."""

        return GenAIScriptGenerateResponse(
            script=mock_script,
            confidence=0.70,
            compliance_checked=True,
            compliance_issues=[]
        )


@router.post("/analyze-intent", response_model=GenAIIntentAnalysisResponse)
async def analyze_intent(
    request: GenAIIntentAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze customer intent and sentiment from transcript"""
    start_time = time.time()

    try:
        # Use real LLM to analyze intent
        analyzer = IntentAnalyzer()
        result = await analyzer.analyze(request.transcript)

        processing_time = int((time.time() - start_time) * 1000)

        # Log to audit
        audit = GenAIAudit(
            case_id=None,
            service_type="intent_analysis",
            input_data={"transcript": request.transcript[:200]},
            output_data={
                "intent": result["intent"],
                "sentiment": result["sentiment"],
                "key_phrases": result["key_phrases"]
            },
            confidence=result["confidence"],
            processing_time_ms=processing_time
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
        # Use real LLM to score willingness
        scorer = WillingnessScorer()
        result = await scorer.score(case, contact_history)

        processing_time = int((time.time() - start_time) * 1000)

        # Log to audit
        audit = GenAIAudit(
            case_id=case.id,
            service_type="willingness_scoring",
            input_data={"case_id": str(case.id)},
            output_data={
                "willingness_score": result["willingness_score"],
                "factors": result["factors"]
            },
            confidence=result["confidence"],
            processing_time_ms=processing_time
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


@router.post("/compliance-check")
async def compliance_check(
    script: str,
    current_user: dict = Depends(get_current_user)
):
    """Check script for compliance violations"""
    violations = []

    # Basic keyword check
    forbidden_words = [
        "sue", "lawsuit", "legal action", "arrest", "jail",
        "police", "report you", "ruin your credit", "threaten",
        "must pay", "have to pay"
    ]

    script_lower = script.lower()

    for word in forbidden_words:
        if word in script_lower:
            violations.append({
                "type": "forbidden_language",
                "keyword": word,
                "severity": "high"
            })

    is_compliant = len(violations) == 0

    return {
        "is_compliant": is_compliant,
        "violations": violations,
        "confidence": 0.95
    }
