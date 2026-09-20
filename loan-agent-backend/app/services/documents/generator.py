"""
Document Generation Service

Generates collection-related documents including:
- Collection letters
- Payment plans
- Legal notices
- Settlement agreements
- Demand letters
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
import os
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Document generation service using Jinja2 templates"""

    def __init__(self, template_dir: str = None):
        """
        Initialize document generator

        Args:
            template_dir: Directory containing document templates
        """
        if template_dir is None:
            template_dir = os.path.join(
                os.path.dirname(__file__),
                "../../templates/documents"
            )

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

        # Add custom filters
        self.env.filters['currency'] = self._currency_filter
        self.env.filters['date'] = self._date_filter

    def _currency_filter(self, value: float) -> str:
        """Format currency values"""
        return f"${value:,.2f}"

    def _date_filter(self, value: Any, format: str = "%B %d, %Y") -> str:
        """Format dates"""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)

    def generate_collection_letter(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        letter_type: str = "initial"
    ) -> str:
        """
        Generate a collection letter

        Args:
            case_data: Case information
            customer_data: Customer information
            letter_type: Type of letter (initial, reminder, final)

        Returns:
            Generated letter content
        """
        template_map = {
            "initial": "collection_letter_initial.html",
            "reminder": "collection_letter_reminder.html",
            "final": "collection_letter_final.html"
        }

        template_name = template_map.get(letter_type, "collection_letter_initial.html")

        # Prepare context
        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "due_date": datetime.now() + timedelta(days=14),
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "phone": "(555) 123-4567",
                "email": "collections@capco.com"
            }
        }

        return self._render_template(template_name, context)

    def generate_payment_plan(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        plan_details: Dict[str, Any]
    ) -> str:
        """
        Generate a payment plan agreement

        Args:
            case_data: Case information
            customer_data: Customer information
            plan_details: Payment plan details (amount, duration, etc.)

        Returns:
            Generated payment plan document
        """
        # Calculate payment schedule
        total_amount = plan_details.get("total_amount")
        num_payments = plan_details.get("num_payments")
        payment_amount = total_amount / num_payments
        start_date = plan_details.get("start_date", datetime.now())

        payments = []
        for i in range(num_payments):
            payment_date = start_date + timedelta(days=30 * i)
            payments.append({
                "number": i + 1,
                "date": payment_date,
                "amount": payment_amount
            })

        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "plan": {
                **plan_details,
                "payment_amount": payment_amount,
                "payments": payments
            },
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }

        return self._render_template("payment_plan.html", context)

    def generate_demand_letter(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        deadline_days: int = 10
    ) -> str:
        """
        Generate a formal demand letter

        Args:
            case_data: Case information
            customer_data: Customer information
            deadline_days: Days until legal action

        Returns:
            Generated demand letter
        """
        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "deadline": datetime.now() + timedelta(days=deadline_days),
            "deadline_days": deadline_days,
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "phone": "(555) 123-4567"
            }
        }

        return self._render_template("demand_letter.html", context)

    def generate_settlement_offer(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        settlement_amount: float,
        original_amount: float,
        expiry_days: int = 30
    ) -> str:
        """
        Generate a settlement offer letter

        Args:
            case_data: Case information
            customer_data: Customer information
            settlement_amount: Offered settlement amount
            original_amount: Original debt amount
            expiry_days: Days until offer expires

        Returns:
            Generated settlement offer
        """
        discount_percentage = ((original_amount - settlement_amount) / original_amount) * 100

        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "settlement_amount": settlement_amount,
            "original_amount": original_amount,
            "discount_percentage": discount_percentage,
            "expiry_date": datetime.now() + timedelta(days=expiry_days),
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "phone": "(555) 123-4567"
            }
        }

        return self._render_template("settlement_offer.html", context)

    def generate_receipt(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        payment_data: Dict[str, Any]
    ) -> str:
        """
        Generate a payment receipt

        Args:
            case_data: Case information
            customer_data: Customer information
            payment_data: Payment details

        Returns:
            Generated receipt
        """
        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "payment": payment_data,
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "phone": "(555) 123-4567"
            }
        }

        return self._render_template("payment_receipt.html", context)

    def generate_cease_and_desist_acknowledgment(
        self,
        case_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> str:
        """
        Generate acknowledgment of cease and desist request

        Args:
            case_data: Case information
            customer_data: Customer information

        Returns:
            Generated acknowledgment letter
        """
        context = {
            "date": datetime.now(),
            "customer": customer_data,
            "case": case_data,
            "company": {
                "name": "Capco Loan Services",
                "address": "123 Financial Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }

        return self._render_template("cease_and_desist_ack.html", context)

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with context

        Args:
            template_name: Name of template file
            context: Template context data

        Returns:
            Rendered content
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Return a fallback simple text version
            return self._generate_fallback_document(template_name, context)

    def _generate_fallback_document(self, doc_type: str, context: Dict[str, Any]) -> str:
        """Generate a simple text fallback when template fails"""
        customer = context.get("customer", {})
        case = context.get("case", {})

        return f"""
CAPCO LOAN SERVICES
{context['date'].strftime('%B %d, %Y')}

{customer.get('name', 'Dear Customer')}
{customer.get('address', '')}

RE: Account #{case.get('case_id', 'N/A')}

This is regarding your outstanding loan balance of ${case.get('overdue_amount', 0):,.2f}.

Please contact us at (555) 123-4567 to discuss payment options.

Sincerely,
Capco Loan Services
Collections Department
"""


# Global document generator instance
document_generator = DocumentGenerator()
