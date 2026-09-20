"""
Willingness to Pay Scorer

Analyzes case factors to predict customer willingness to pay
"""
from typing import Dict, Any, List
from app.services.genai.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class WillingnessScorer:
    """Score customer willingness to pay using GenAI"""

    def __init__(self):
        self.llm_client = LLMClient()

    async def score_willingness(
        self,
        case_data: Dict[str, Any],
        conversation_history: List[str] = None
    ) -> Dict[str, Any]:
        """
        Score customer willingness to pay (0-10 scale)

        Args:
            case_data: Case information
            conversation_history: Optional conversation transcripts

        Returns:
            {
                "score": 7.5,
                "confidence": 0.85,
                "factors": [
                    {
                        "factor": "Recent positive engagement",
                        "impact": +2,
                        "explanation": "Customer responded quickly"
                    }
                ],
                "recommendation": "Offer payment plan",
                "processing_time_ms": 1500
            }
        """
        import time
        start_time = time.time()

        # Build analysis prompt
        prompt = self._build_prompt(case_data, conversation_history)

        # Get LLM response
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=800
        )

        # Parse response
        result = self._parse_response(response)

        # Add processing time
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)

        logger.info(
            f"Willingness score for case {case_data.get('case_id')}: "
            f"{result['score']}/10 (confidence: {result['confidence']})"
        )

        return result

    def _build_prompt(
        self,
        case_data: Dict[str, Any],
        conversation_history: List[str] = None
    ) -> str:
        """Build prompt for willingness scoring"""

        prompt = f"""Analyze this customer's willingness to pay their overdue loan and provide a score from 0-10.

**Case Information:**
- Overdue Amount: ${case_data.get('overdue_amount', 0):,.2f}
- Days Overdue: {case_data.get('overdue_days', 0)}
- Contact Attempts: {case_data.get('contact_count', 0)}
- Status: {case_data.get('status', 'unknown')}
- Loan Product: {case_data.get('loan_product', 'unknown')}"""

        if conversation_history:
            prompt += f"\n\n**Recent Conversations:**\n"
            for i, conv in enumerate(conversation_history[-3:], 1):
                prompt += f"{i}. {conv}\n"

        prompt += """

**Scoring Criteria:**
- 9-10: Very likely to pay, proactive engagement
- 7-8: Likely to pay, responsive to contact
- 5-6: Uncertain, mixed signals
- 3-4: Unlikely to pay, avoiding contact
- 0-2: Very unlikely, no engagement

**Provide your analysis in this format:**

SCORE: [0-10]
CONFIDENCE: [0.0-1.0]

FACTORS:
- [Factor name]: [+/- impact] - [explanation]
- [Factor name]: [+/- impact] - [explanation]

RECOMMENDATION:
[What action to take next]
"""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        import re

        result = {
            "score": 5.0,
            "confidence": 0.5,
            "factors": [],
            "recommendation": ""
        }

        try:
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', response)
            if score_match:
                result["score"] = float(score_match.group(1))

            # Extract confidence
            conf_match = re.search(r'CONFIDENCE:\s*(\d+(?:\.\d+)?)', response)
            if conf_match:
                result["confidence"] = float(conf_match.group(1))

            # Extract factors
            factors_section = re.search(
                r'FACTORS:(.*?)(?:RECOMMENDATION:|$)',
                response,
                re.DOTALL
            )
            if factors_section:
                factors_text = factors_section.group(1)
                factor_lines = [
                    line.strip()
                    for line in factors_text.split('\n')
                    if line.strip() and line.strip().startswith('-')
                ]

                for line in factor_lines:
                    # Parse factor line: "- Factor: +2 - explanation"
                    factor_match = re.match(
                        r'-\s*([^:]+):\s*([\+\-]\d+)\s*-\s*(.+)',
                        line
                    )
                    if factor_match:
                        result["factors"].append({
                            "factor": factor_match.group(1).strip(),
                            "impact": int(factor_match.group(2)),
                            "explanation": factor_match.group(3).strip()
                        })

            # Extract recommendation
            rec_match = re.search(
                r'RECOMMENDATION:\s*(.+?)(?:\n\n|$)',
                response,
                re.DOTALL
            )
            if rec_match:
                result["recommendation"] = rec_match.group(1).strip()

        except Exception as e:
            logger.error(f"Error parsing willingness score response: {str(e)}")

        return result


# Global instance
willingness_scorer = WillingnessScorer()
