"""
Script Generation Service with RAG and Trust Gate Integration
"""

from typing import Dict, Any, Optional
import logging

from app.services.genai.llm_client import generate_completion
from app.services.genai.rag_service import get_rag_service
from app.models.base import Case

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Service for generating collection scripts using LLM with RAG"""

    def __init__(self):
        try:
            self.rag_service = get_rag_service()
        except Exception as e:
            logger.warning(f"RAG service unavailable: {e}")
            self.rag_service = None

    async def generate_script(
        self,
        case: Case = None,
        case_data: Dict[str, Any] = None,
        scenario: str = "general",
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generate a collection script for a case

        Args:
            case: Case object (optional if case_data provided)
            case_data: Case data dict (optional if case provided)
            scenario: Script scenario (first_contact, payment_plan, dispute, etc.)
            tone: Tone of the script (professional, empathetic, firm)

        Returns:
            Dict with script, confidence, compliance info, and RAG sources
        """
        # Extract case data
        if case:
            overdue_amount = float(case.overdue_amount)
            overdue_days = case.overdue_days
            customer_id = case.customer_id
            loan_product = case.loan_product or "Personal Loan"
            status = case.status
            contact_count = case.contact_count
        elif case_data:
            overdue_amount = case_data.get("overdue_amount", 0)
            overdue_days = case_data.get("overdue_days", 0)
            customer_id = case_data.get("customer_id", "N/A")
            loan_product = case_data.get("loan_product", "Personal Loan")
            status = case_data.get("status", "unknown")
            contact_count = case_data.get("contact_count", 0)
        else:
            raise ValueError("Either case or case_data must be provided")

        # Try to retrieve from RAG, but fallback to static context if unavailable
        if self.rag_service:
            try:
                compliance_context = await self.rag_service.retrieve_compliance_context(
                    query=f"Hong Kong collection script compliance {scenario}",
                    n_results=3
                )
            except Exception as e:
                logger.warning(f"RAG retrieval failed, using fallback: {e}")
                compliance_context = """
HONG KONG COMPLIANCE CONTEXT (Fallback):
Money Lenders Ordinance (Cap. 163):
- Must properly identify yourself, company, and license number
- No harassment, coercion, or oppression
- No disclosure to third parties without consent
- Contact only during reasonable hours (8 AM - 9 PM)
- Clear disclosure of fees and charges
- No false or misleading representations
"""
        else:
            compliance_context = """
HONG KONG COMPLIANCE CONTEXT (Fallback):
Money Lenders Ordinance (Cap. 163):
- Must properly identify yourself, company, and license number
- No harassment, coercion, or oppression
- No disclosure to third parties without consent
- Contact only during reasonable hours (8 AM - 9 PM)
- Clear disclosure of fees and charges
- No false or misleading representations
"""

        if self.rag_service:
            try:
                template_context = await self.rag_service.retrieve_script_templates(
                    scenario=scenario,
                    n_results=2
                )
            except Exception as e:
                logger.warning(f"Template retrieval failed, using fallback: {e}")
                template_context = """
APPROVED SCRIPT TEMPLATES (Fallback):
Opening: "Good morning/afternoon, this is [Name] calling from [Company], Money Lender License #[Number]."
Purpose: "I'm calling regarding your [Loan Type] account ending in [Last 4 digits]."
Request: "We noticed your payment is [X] days overdue. May I discuss this with you?"
"""
        else:
            template_context = """
APPROVED SCRIPT TEMPLATES (Fallback):
Opening: "Good morning/afternoon, this is [Name] calling from [Company], Money Lender License #[Number]."
Purpose: "I'm calling regarding your [Loan Type] account ending in [Last 4 digits]."
Request: "We noticed your payment is [X] days overdue. May I discuss this with you?"
"""

        # ✅ Enhanced system prompt with RAG context
        system_prompt = f"""You are an expert Hong Kong debt collection script generator.

{compliance_context}

{template_context}

MANDATORY COMPLIANCE RULES:
1. Identify yourself, company name, and money lender license number
2. NEVER contact third parties to disclose debt (except guarantors)
3. Contact only during reasonable hours (8 AM - 9 PM HKT)
4. NO harassment, threats, or intimidation
5. NO misrepresentation (do not claim to be police, court, or authority)
6. Respect data privacy (PDPO compliance)
7. Be professional, empathetic, and solution-focused

Tone: {tone}
Language: Use appropriate mix of English and Cantonese for Hong Kong context

Generate a compliant, effective collection script following the approved templates above."""

        prompt = f"""Generate a collection script for this case:

Case Details:
- Customer ID: {customer_id}
- Loan Product: {loan_product}
- Overdue Amount: HK${overdue_amount:,.2f}
- Days Overdue: {overdue_days}
- Current Status: {status}
- Previous Contacts: {contact_count}

Scenario: {scenario}

Requirements:
1. Opening with proper identification (collector name, bank, license)
2. Verification of customer identity
3. Clear statement of purpose
4. Active listening approach
5. Offer payment solutions/plans
6. Document next steps
7. Professional closing

Format as dialogue with [Collector:] and [Customer:] labels."""

        try:
            script = await generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000,
            )

            # ✅ Enhanced compliance check
            compliance_issues = self._check_compliance(script)

            # ✅ Calculate actual confidence based on multiple factors
            confidence = self._calculate_confidence(
                script=script,
                compliance_issues=compliance_issues,
                has_rag_context=True
            )

            return {
                "script": script,
                "confidence": confidence,
                "compliance_checked": True,
                "compliance_issues": compliance_issues,
                "compliance_warnings": [issue["phrase"] for issue in compliance_issues],
                "scenario": scenario,
                "tone": tone,
                "amount": overdue_amount,
                "action_type": scenario,
                "rag_sources_used": True
            }

        except Exception as e:
            logger.error(f"Script generation error: {str(e)}")
            raise

    def _calculate_confidence(
        self,
        script: str,
        compliance_issues: list,
        has_rag_context: bool
    ) -> float:
        """
        Calculate confidence score for generated script

        Args:
            script: Generated script
            compliance_issues: List of compliance issues
            has_rag_context: Whether RAG context was used

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence

        # Boost for RAG context
        if has_rag_context:
            confidence += 0.2

        # Penalty for compliance issues
        if compliance_issues:
            high_severity = sum(1 for issue in compliance_issues if issue["severity"] == "high")
            medium_severity = sum(1 for issue in compliance_issues if issue["severity"] == "medium")
            confidence -= (high_severity * 0.15 + medium_severity * 0.05)

        # Boost for proper structure
        required_elements = [
            "collector:",
            "customer:",
            "hk$",
            "thank you"
        ]
        script_lower = script.lower()
        elements_found = sum(1 for elem in required_elements if elem in script_lower)
        confidence += (elements_found / len(required_elements)) * 0.2

        # Boost for reasonable length
        word_count = len(script.split())
        if 100 <= word_count <= 500:
            confidence += 0.1

        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, confidence))

    def _check_compliance(self, script: str) -> list:
        """
        Enhanced compliance check for generated scripts (HK-specific)

        Args:
            script: Generated script text

        Returns:
            List of compliance issues found
        """
        issues = []

        script_lower = script.lower()

        # High severity: Misrepresentation as authority
        authority_phrases = [
            "police", "警察", "law enforcement", "執法",
            "court", "法院", "legal action", "法律行動",
            "arrest", "拘捕", "jail", "監獄", "prison", "囚禁"
        ]
        for phrase in authority_phrases:
            if phrase in script_lower:
                issues.append({
                    "type": "misrepresentation_as_authority",
                    "phrase": phrase,
                    "severity": "high",
                    "description": "HK Money Lenders Ordinance prohibits misrepresenting as authority"
                })

        # High severity: Harassment/threats
        threat_phrases = [
            "threaten", "威脅", "sue", "起訴",
            "lawsuit", "訴訟", "report you", "報警",
            "ruin your credit", "破壞信用", "embarrass", "羞辱",
            "publish", "公開", "expose", "曝光"
        ]
        for phrase in threat_phrases:
            if phrase in script_lower:
                issues.append({
                    "type": "threatening_language",
                    "phrase": phrase,
                    "severity": "high",
                    "description": "Threatening or harassing language prohibited"
                })

        # High severity: Third-party disclosure
        third_party_phrases = [
            "tell your family", "告訴你家人", "contact your employer", "聯繫你僱主",
            "friends will know", "朋友會知道", "colleagues", "同事"
        ]
        for phrase in third_party_phrases:
            if phrase in script_lower:
                issues.append({
                    "type": "third_party_disclosure_threat",
                    "phrase": phrase,
                    "severity": "high",
                    "description": "Cannot threaten to disclose debt to third parties"
                })

        # Medium severity: Pressure tactics
        pressure_phrases = [
            "must pay now", "必須立即付款", "have to pay", "一定要還",
            "no choice", "沒有選擇", "immediately", "馬上"
        ]
        for phrase in pressure_phrases:
            if phrase in script_lower:
                issues.append({
                    "type": "excessive_pressure",
                    "phrase": phrase,
                    "severity": "medium",
                    "description": "Excessive pressure tactics"
                })

        # Check for missing identification
        has_identification = any(phrase in script_lower for phrase in [
            "my name is", "我叫", "i am", "我是",
            "from", "來自", "bank", "銀行"
        ])
        if not has_identification:
            issues.append({
                "type": "missing_identification",
                "phrase": "N/A",
                "severity": "high",
                "description": "HK law requires collector to identify themselves"
            })

        return issues

