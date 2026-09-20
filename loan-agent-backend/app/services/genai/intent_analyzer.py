"""
Intent and Sentiment Analysis Service
"""

from typing import Dict, Any, List
import logging
import json

from app.services.genai.llm_client import generate_completion

logger = logging.getLogger(__name__)


class IntentAnalyzer:
    """Service for analyzing customer intent and sentiment"""

    async def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze customer intent and sentiment from conversation transcript

        Args:
            transcript: Conversation transcript text

        Returns:
            Dict with intent, sentiment, confidence, and key phrases
        """
        system_prompt = """You are an AI assistant analyzing customer conversations in loan collection.
Analyze the customer's intent and sentiment from the transcript.

Respond with a JSON object containing:
{
    "intent": "one of: willing_to_pay, needs_time, dispute, financial_hardship, refusing_to_pay, unreachable",
    "sentiment": "one of: positive, neutral, negative, angry, cooperative",
    "confidence": 0.0-1.0,
    "key_phrases": ["list", "of", "important", "phrases"],
    "reasoning": "brief explanation"
}"""

        prompt = f"""Analyze this conversation transcript:

{transcript}

Provide the analysis in JSON format as specified."""

        try:
            response = await generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500,
            )

            # Parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                result = json.loads(response)

                return {
                    "intent": result.get("intent", "unknown"),
                    "sentiment": result.get("sentiment", "neutral"),
                    "confidence": result.get("confidence", 0.7),
                    "key_phrases": result.get("key_phrases", []),
                    "reasoning": result.get("reasoning", ""),
                }

            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {response}")
                # Fallback to basic analysis
                return self._fallback_analysis(transcript)

        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            raise

    def _fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Fallback analysis if JSON parsing fails"""
        transcript_lower = transcript.lower()

        # Simple keyword-based analysis
        intent = "unknown"
        sentiment = "neutral"

        if any(
            word in transcript_lower
            for word in ["pay", "payment", "settle", "arrange"]
        ):
            intent = "willing_to_pay"
            sentiment = "positive"
        elif any(word in transcript_lower for word in ["need time", "next month", "soon"]):
            intent = "needs_time"
            sentiment = "neutral"
        elif any(word in transcript_lower for word in ["dispute", "wrong", "error"]):
            intent = "dispute"
            sentiment = "negative"
        elif any(
            word in transcript_lower
            for word in ["can't afford", "no money", "lost job"]
        ):
            intent = "financial_hardship"
            sentiment = "negative"

        return {
            "intent": intent,
            "sentiment": sentiment,
            "confidence": 0.5,
            "key_phrases": [],
            "reasoning": "Fallback analysis based on keywords",
        }


class WillingnessScorer:
    """Service for scoring customer willingness to pay"""

    async def score(self, case: Any, contact_history: List[Any]) -> Dict[str, Any]:
        """
        Score customer's willingness to pay based on case and history

        Args:
            case: Case object
            contact_history: List of contact history records

        Returns:
            Dict with willingness score, factors, and recommendation
        """
        system_prompt = """You are an AI assistant scoring customer willingness to pay.
Analyze the case information and contact history to provide a willingness score.

Respond with a JSON object:
{
    "willingness_score": 0.0-1.0,
    "factors": {
        "contact_responsiveness": 0.0-1.0,
        "payment_history": 0.0-1.0,
        "communication_tone": 0.0-1.0,
        "promise_keeping": 0.0-1.0
    },
    "confidence": 0.0-1.0,
    "recommendation": "brief recommendation"
}"""

        # Build context
        contact_summary = "\n".join(
            [
                f"- {c.contact_type} on {c.contact_time}: {c.outcome} (sentiment: {c.sentiment})"
                for c in contact_history[:10]  # Last 10 contacts
            ]
        )

        prompt = f"""Score this customer's willingness to pay:

Case Information:
- Overdue Days: {case.overdue_days}
- Overdue Amount: ${case.overdue_amount:,.2f}
- Status: {case.status}
- Contact Count: {case.contact_count}
- Dispute Flag: {case.dispute_flag}

Recent Contact History:
{contact_summary if contact_summary else 'No contact history'}

Provide the scoring analysis in JSON format."""

        try:
            response = await generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=600,
            )

            # Parse JSON response
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                result = json.loads(response)

                return {
                    "willingness_score": result.get("willingness_score", 0.5),
                    "factors": result.get("factors", {}),
                    "confidence": result.get("confidence", 0.7),
                    "recommendation": result.get("recommendation", ""),
                }

            except json.JSONDecodeError:
                logger.warning(f"Failed to parse scoring JSON: {response}")
                return self._fallback_scoring(case, contact_history)

        except Exception as e:
            logger.error(f"Willingness scoring error: {str(e)}")
            raise

    def _fallback_scoring(self, case: Any, contact_history: List[Any]) -> Dict[str, Any]:
        """Fallback scoring if JSON parsing fails"""
        # Simple rule-based scoring
        score = 0.5

        if case.contact_count > 0:
            score += 0.1
        if case.overdue_days < 30:
            score += 0.2
        if not case.dispute_flag:
            score += 0.1

        score = min(1.0, max(0.0, score))

        return {
            "willingness_score": score,
            "factors": {
                "contact_responsiveness": 0.5,
                "payment_history": 0.5,
                "communication_tone": 0.5,
                "promise_keeping": 0.5,
            },
            "confidence": 0.5,
            "recommendation": "Fallback scoring - requires manual review",
        }
