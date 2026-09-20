"""
Customer-Facing Chatbot Service
AI-powered chatbot for customer self-service and payment arrangements
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.genai.llm_client import get_llm_client
from app.services.genai.rag_service import get_rag_service
from app.services.genai.intent_analyzer import IntentAnalyzer
from app.models.case import Case

logger = logging.getLogger(__name__)


class CollectionChatbot:
    """
    Customer-facing chatbot for debt collection
    Handles inquiries, payment arrangements, and dispute resolution
    """

    def __init__(self):
        self.llm_client = get_llm_client()
        self.rag_service = get_rag_service()
        self.intent_analyzer = IntentAnalyzer()
        self.conversation_history = {}

    async def chat(
        self,
        message: str,
        session_id: str,
        case: Optional[Case] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process customer message and generate response

        Args:
            message: Customer message
            session_id: Conversation session ID
            case: Associated case (if identified)
            context: Additional context

        Returns:
            Chatbot response with intent, actions, and next steps
        """
        # Analyze intent
        intent_result = await self.intent_analyzer.analyze(message)

        # Get conversation history
        history = self.conversation_history.get(session_id, [])

        # Retrieve relevant context from RAG
        compliance_context = await self.rag_service.retrieve_compliance_context(
            query=f"customer inquiry about {intent_result.get('intent', 'payment')}",
            n_results=2
        )

        # Build chatbot system prompt
        system_prompt = self._build_system_prompt(
            case=case,
            compliance_context=compliance_context,
            intent=intent_result.get('intent')
        )

        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add history
        for msg in history[-5:]:  # Last 5 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            # Generate response
            response = await self.llm_client.complete(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            bot_message = response["content"]

            # Update conversation history
            history.append({"role": "user", "content": message, "timestamp": datetime.utcnow().isoformat()})
            history.append({"role": "assistant", "content": bot_message, "timestamp": datetime.utcnow().isoformat()})
            self.conversation_history[session_id] = history

            # Determine actions
            actions = self._determine_actions(intent_result, message, bot_message)

            # Compliance check
            requires_human = self._requires_human_takeover(
                intent_result,
                message,
                case
            )

            return {
                "message": bot_message,
                "intent": intent_result.get("intent"),
                "sentiment": intent_result.get("sentiment"),
                "confidence": intent_result.get("confidence"),
                "actions": actions,
                "requires_human_takeover": requires_human,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return {
                "message": "I apologize, but I'm having trouble right now. Let me connect you with a representative.",
                "requires_human_takeover": True,
                "error": str(e)
            }

    def _build_system_prompt(
        self,
        case: Optional[Case],
        compliance_context: str,
        intent: Optional[str]
    ) -> str:
        """Build system prompt for chatbot"""
        case_info = ""
        if case:
            case_info = f"""
CUSTOMER ACCOUNT INFORMATION:
- Account Number: {case.case_id}
- Outstanding Amount: HK${case.overdue_amount:,.2f}
- Days Overdue: {case.overdue_days}
- Status: {case.status}
"""

        return f"""You are a helpful and empathetic customer service assistant for a Hong Kong financial institution's debt collection department.

YOUR ROLE:
- Help customers understand their account status
- Assist with payment arrangements
- Answer questions about payment options
- Handle disputes professionally
- Provide clear information about policies

{compliance_context}

{case_info}

IMPORTANT GUIDELINES:
1. Be polite, empathetic, and professional at all times
2. Never threaten, harass, or use aggressive language
3. Clearly identify yourself as a representative of the bank
4. Respect customer privacy (PDPO compliance)
5. Offer payment plans and solutions
6. If customer disputes the debt, escalate to human representative
7. If customer mentions financial hardship, show empathy and offer options
8. Always comply with Money Lenders Ordinance requirements

TONE: Professional, helpful, empathetic
LANGUAGE: Use both English and Cantonese as appropriate for the customer

If the customer becomes hostile or the situation is complex, recommend connecting with a human representative.
"""

    def _determine_actions(
        self,
        intent_result: Dict[str, Any],
        message: str,
        bot_response: str
    ) -> List[str]:
        """Determine actions to take based on conversation"""
        actions = []

        intent = intent_result.get("intent", "")

        if intent == "payment":
            actions.append("offer_payment_options")
            if "plan" in message.lower() or "installment" in message.lower():
                actions.append("suggest_payment_plan")

        elif intent == "dispute":
            actions.append("escalate_to_human")
            actions.append("create_dispute_ticket")

        elif intent == "financial_hardship":
            actions.append("offer_hardship_options")
            actions.append("schedule_callback")

        elif intent == "information":
            actions.append("provide_account_details")

        # Check if payment was mentioned
        if any(word in message.lower() for word in ["pay", "payment", "settle", "clear"]):
            actions.append("generate_payment_link")

        return actions

    def _requires_human_takeover(
        self,
        intent_result: Dict[str, Any],
        message: str,
        case: Optional[Case]
    ) -> bool:
        """Determine if human takeover is required"""
        # High-risk intents
        high_risk_intents = ["dispute", "complaint", "legal", "harassment"]
        if intent_result.get("intent") in high_risk_intents:
            return True

        # Negative sentiment
        if intent_result.get("sentiment") == "negative":
            return True

        # Complex cases
        if case and float(case.overdue_amount) > 100000:
            return True

        # Hostile language
        hostile_keywords = ["lawyer", "sue", "report", "complain", "harassment"]
        if any(word in message.lower() for word in hostile_keywords):
            return True

        return False

    async def generate_payment_link(
        self,
        case_id: str,
        amount: float,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate secure payment link for customer

        Args:
            case_id: Case ID
            amount: Payment amount
            session_id: Session ID

        Returns:
            Payment link and details
        """
        # In production, integrate with payment gateway
        payment_id = f"PAY-{case_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        return {
            "payment_id": payment_id,
            "payment_link": f"https://payments.bank.com/pay/{payment_id}",
            "amount": amount,
            "expires_at": (datetime.utcnow().timestamp() + 3600),  # 1 hour
            "qr_code_url": f"https://payments.bank.com/qr/{payment_id}",
            "instructions": "Click the link or scan QR code to make payment securely"
        }

    async def offer_payment_plan(
        self,
        case: Case,
        customer_proposed_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate payment plan options

        Args:
            case: Case details
            customer_proposed_amount: Customer's proposed monthly payment

        Returns:
            Payment plan options
        """
        total_amount = float(case.overdue_amount)

        # Generate 3 plan options
        plans = [
            {
                "name": "3-Month Plan",
                "duration_months": 3,
                "monthly_payment": total_amount / 3,
                "total_amount": total_amount,
                "recommended": total_amount < 50000
            },
            {
                "name": "6-Month Plan",
                "duration_months": 6,
                "monthly_payment": total_amount / 6,
                "total_amount": total_amount,
                "recommended": 50000 <= total_amount < 100000
            },
            {
                "name": "12-Month Plan",
                "duration_months": 12,
                "monthly_payment": total_amount / 12,
                "total_amount": total_amount,
                "recommended": total_amount >= 100000
            }
        ]

        # If customer proposed amount, calculate custom plan
        if customer_proposed_amount:
            months_needed = int(total_amount / customer_proposed_amount) + 1
            plans.append({
                "name": "Custom Plan",
                "duration_months": months_needed,
                "monthly_payment": customer_proposed_amount,
                "total_amount": total_amount,
                "recommended": False
            })

        return {
            "case_id": case.case_id,
            "total_amount": total_amount,
            "plans": plans,
            "note": "Payment plans subject to approval. No additional interest charges."
        }

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

    async def get_conversation_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate summary of conversation for agent review

        Args:
            session_id: Session ID

        Returns:
            Conversation summary
        """
        history = self.conversation_history.get(session_id, [])

        if not history:
            return {"summary": "No conversation history"}

        # Build summary prompt
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in history
        ])

        system_prompt = """Summarize this customer service conversation.
Include: customer's main concern, bot's response, any actions taken, and recommended next steps.
Keep it concise (under 150 words)."""

        response = await self.llm_client.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summarize this conversation:\n\n{conversation_text}"}
            ],
            temperature=0.3,
            max_tokens=300
        )

        return {
            "session_id": session_id,
            "summary": response["content"],
            "message_count": len(history),
            "duration_minutes": self._calculate_duration(history),
            "last_updated": history[-1]["timestamp"] if history else None
        }

    def _calculate_duration(self, history: List[Dict]) -> float:
        """Calculate conversation duration in minutes"""
        if len(history) < 2:
            return 0

        start = datetime.fromisoformat(history[0]["timestamp"])
        end = datetime.fromisoformat(history[-1]["timestamp"])
        return (end - start).total_seconds() / 60


# Singleton instance
_chatbot: Optional[CollectionChatbot] = None


def get_chatbot() -> CollectionChatbot:
    """Get or create chatbot singleton"""
    global _chatbot

    if _chatbot is None:
        _chatbot = CollectionChatbot()

    return _chatbot
