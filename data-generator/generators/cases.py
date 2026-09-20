"""
Case Generator - Generate Collection Cases
"""
import random
from datetime import datetime, timedelta
from typing import Dict
import json
import os


class CaseGenerator:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        with open(os.path.join(template_dir, 'loan_products.json'), 'r') as f:
            self.loan_products = json.load(f)

    def determine_status(self, overdue_days: int) -> str:
        """Determine case status based on overdue days"""
        if overdue_days <= 30:
            return "new"
        elif overdue_days <= 90:
            return "in_progress"
        elif overdue_days <= 180:
            return "escalated"
        else:
            return "legal_review"

    def calculate_priority(self, overdue_amount: float, overdue_days: int,
                          customer_segment: str) -> int:
        """Calculate case priority (1-10)"""
        priority = 5  # Base priority

        # Amount factor
        if overdue_amount > 100000:
            priority += 3
        elif overdue_amount > 50000:
            priority += 2
        elif overdue_amount > 10000:
            priority += 1

        # Days factor
        if overdue_days > 180:
            priority += 3
        elif overdue_days > 90:
            priority += 2
        elif overdue_days > 30:
            priority += 1

        # Customer segment
        if customer_segment == "VIP":
            priority += 2
        elif customer_segment == "premium":
            priority += 1

        return min(priority, 10)  # Cap at 10

    def select_assignee(self, priority: int, overdue_amount: float) -> str:
        """Select collector based on case characteristics"""
        # Return None - assigned_to needs to be a UUID, not a string
        # We'll leave cases unassigned for now
        return None

    def generate_case(self, customer_id: str, customer_segment: str = "standard") -> Dict:
        """Generate a collection case"""
        case_id = f"CASE{random.randint(100000, 999999)}"
        loan_id = f"LOAN{random.randint(100000, 999999)}"

        # Generate realistic overdue scenario
        overdue_days = random.choices(
            [
                random.randint(1, 15),    # Early stage
                random.randint(16, 30),   # Standard early
                random.randint(31, 60),   # Mid-stage
                random.randint(61, 90),   # Late stage
                random.randint(91, 180),  # Very late
                random.randint(181, 365)  # Critical
            ],
            weights=[30, 25, 20, 15, 8, 2]
        )[0]

        # Generate loan amount based on product
        loan_product = random.choice(self.loan_products['products'])
        principal_amount = random.randint(
            loan_product['min_amount'],
            loan_product['max_amount']
        )

        # Overdue amount (could be full or partial)
        overdue_ratio = random.uniform(0.1, 1.0)
        overdue_amount = round(principal_amount * overdue_ratio, 2)

        status = self.determine_status(overdue_days)
        priority = self.calculate_priority(overdue_amount, overdue_days, customer_segment)
        assignee = self.select_assignee(priority, overdue_amount)

        # Contact history stats
        contact_count = min(overdue_days // 7, 15)  # Roughly weekly contacts
        contact_success_rate = random.uniform(0.1, 0.9)

        return {
            'case_id': case_id,
            'customer_id': customer_id,
            'loan_id': loan_id,
            'loan_product': loan_product['name'],
            'principal_amount': principal_amount,
            'overdue_amount': overdue_amount,
            'overdue_days': overdue_days,
            'status': status,
            'priority': priority,
            'assigned_to': assignee,
            'contact_count': contact_count,
            'contact_success_rate': contact_success_rate,
            'dispute_flag': random.random() < 0.05,  # 5% have disputes
            'payment_promise_kept': random.random() < 0.6,  # 60% keep promises
            'created_at': datetime.now() - timedelta(days=overdue_days),
            'last_contact_date': datetime.now() - timedelta(days=random.randint(1, min(overdue_days, 30)))
        }
