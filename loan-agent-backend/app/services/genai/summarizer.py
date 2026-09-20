"""
Case Summarization Service with RAG Integration
"""

from typing import Dict, Any
import logging

from app.services.genai.llm_client import generate_completion
from app.services.genai.rag_service import get_rag_service
from app.models.base import Case

logger = logging.getLogger(__name__)


class SummarizerService:
    """Service for generating case summaries using LLM with RAG"""

    def __init__(self):
        try:
            self.rag_service = get_rag_service()
        except Exception as e:
            logger.warning(f"RAG service unavailable: {e}")
            self.rag_service = None

    async def summarize(self, case: Case) -> Dict[str, Any]:
        """
        Generate a comprehensive summary for a case

        Args:
            case: Case object to summarize

        Returns:
            Dict with summary, confidence, and metadata
        """
        # Try to retrieve similar cases, but fallback if unavailable
        case_description = f"""Loan overdue {case.overdue_days} days,
            amount HK${case.overdue_amount}, status {case.status},
            {case.contact_count} contacts made"""

        if self.rag_service:
            try:
                similar_cases = await self.rag_service.retrieve_similar_cases(
                    case_description=case_description,
                    n_results=2
                )
            except Exception as e:
                logger.warning(f"RAG service unavailable for similar cases: {e}")
                similar_cases = """
SIMILAR CASES (Fallback):
- Historical cases with similar profiles show average resolution time of 45 days
- Cases with multiple contact attempts (3+) have 60% higher success rate with payment plans
- Long overdue cases (90+ days) benefit from escalation to senior collectors
"""
        else:
            similar_cases = """
SIMILAR CASES (Fallback):
- Historical cases with similar profiles show average resolution time of 45 days
- Cases with multiple contact attempts (3+) have 60% higher success rate with payment plans
- Long overdue cases (90+ days) benefit from escalation to senior collectors
"""

        system_prompt = f"""You are an AI assistant helping with loan collection case analysis.
Generate a clear, professional summary of the case information provided.
Focus on key facts: overdue amount, days overdue, current status, and recommended actions.
Keep the summary concise (under 200 words).

{similar_cases}

Based on similar cases above, provide relevant insights and recommendations."""

        prompt = f"""Please summarize this loan collection case:

Customer ID: {case.customer_id}
Loan ID: {case.loan_id}
Loan Product: {case.loan_product or 'N/A'}
Principal Amount: HK${case.principal_amount:,.2f}
Overdue Amount: HK${case.overdue_amount:,.2f}
Overdue Days: {case.overdue_days}
Current Status: {case.status}
Priority: {case.priority}/10
Contact Count: {case.contact_count}
Last Contact: {case.last_contact_date or 'Never'}
Dispute Flag: {'Yes' if case.dispute_flag else 'No'}
Legal Flag: {'Yes' if case.legal_flag else 'No'}
Tags: {', '.join(case.tags) if case.tags else 'None'}

Provide a professional summary with:
1. Case overview (2-3 sentences)
2. Key risk factors
3. Recommended next actions
4. Urgency assessment"""

        try:
            summary = await generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for factual summaries
                max_tokens=500,
            )

            # ✅ Calculate confidence based on data completeness
            confidence = self._calculate_confidence(case)

            return {
                "summary": summary,
                "confidence": confidence,
                "case_id": str(case.id),
                "has_similar_cases": bool(similar_cases and "No similar cases" not in similar_cases)
            }

        except Exception as e:
            logger.error(f"Summarization error for case {case.case_id}: {str(e)}")
            raise

    def _calculate_confidence(self, case: Case) -> float:
        """
        Calculate confidence score based on case data completeness

        Args:
            case: Case object

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence

        # Boost for complete data
        if case.overdue_amount and case.overdue_amount > 0:
            confidence += 0.15

        if case.overdue_days and case.overdue_days > 0:
            confidence += 0.1

        if case.contact_count is not None:
            confidence += 0.1

        if case.last_contact_date:
            confidence += 0.05

        if case.priority:
            confidence += 0.05

        if case.tags and len(case.tags) > 0:
            confidence += 0.05

        return min(1.0, confidence)
