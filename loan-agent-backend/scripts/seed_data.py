"""
Seed Database with Initial Data

Creates initial users, sample cases, and customers for development/testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models import User, Customer, Case
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid


async def create_users(db: AsyncSession):
    """Create default users"""
    print("Creating users...")

    users = [
        {
            "username": "admin",
            "email": "admin@capco.com",
            "full_name": "Admin User",
            "role": "admin",
            "password": "admin123",
            "is_superuser": True
        },
        {
            "username": "supervisor1",
            "email": "supervisor1@capco.com",
            "full_name": "John Supervisor",
            "role": "supervisor",
            "password": "admin123"
        },
        {
            "username": "collector1",
            "email": "collector1@capco.com",
            "full_name": "Jane Collector",
            "role": "collector",
            "password": "admin123"
        },
        {
            "username": "collector2",
            "email": "collector2@capco.com",
            "full_name": "Mike Collector",
            "role": "collector",
            "password": "admin123"
        }
    ]

    created = 0
    for user_data in users:
        password = user_data.pop("password")
        user = User(
            **user_data,
            hashed_password=get_password_hash(password)
        )
        db.add(user)
        created += 1

    await db.commit()
    print(f"✅ Created {created} users")


async def create_customers(db: AsyncSession):
    """Create sample customers"""
    print("Creating customers...")

    customers = [
        {
            "customer_id": "CUST001",
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john.smith@example.com",
            "id_number": "SSN-123-45-6789",
            "address": "123 Main St, Anytown, CA 90210",
            "credit_score": 650,
            "risk_category": "medium"
        },
        {
            "customer_id": "CUST002",
            "name": "Sarah Johnson",
            "phone": "+1-555-0102",
            "email": "sarah.j@example.com",
            "id_number": "SSN-234-56-7890",
            "address": "456 Oak Ave, Springfield, IL 62701",
            "credit_score": 580,
            "risk_category": "high"
        },
        {
            "customer_id": "CUST003",
            "name": "Michael Brown",
            "phone": "+1-555-0103",
            "email": "mbrown@example.com",
            "id_number": "SSN-345-67-8901",
            "address": "789 Pine Rd, Portland, OR 97201",
            "credit_score": 720,
            "risk_category": "low"
        },
        {
            "customer_id": "CUST004",
            "name": "Emily Davis",
            "phone": "+1-555-0104",
            "email": "emily.d@example.com",
            "id_number": "SSN-456-78-9012",
            "address": "321 Elm St, Boston, MA 02101",
            "credit_score": 600,
            "risk_category": "medium"
        },
        {
            "customer_id": "CUST005",
            "name": "Robert Wilson",
            "phone": "+1-555-0105",
            "email": "r.wilson@example.com",
            "id_number": "SSN-567-89-0123",
            "address": "654 Maple Dr, Seattle, WA 98101",
            "credit_score": 550,
            "risk_category": "high"
        }
    ]

    created = 0
    for customer_data in customers:
        customer = Customer(**customer_data)
        db.add(customer)
        created += 1

    await db.commit()
    print(f"✅ Created {created} customers")


async def create_cases(db: AsyncSession):
    """Create sample cases"""
    print("Creating cases...")

    cases = [
        {
            "case_id": "CASE001",
            "customer_id": "CUST001",
            "loan_id": "LOAN001",
            "loan_product": "Personal Loan",
            "principal_amount": 50000.00,
            "overdue_amount": 5000.00,
            "overdue_days": 45,
            "status": "new",
            "priority": 7,
            "contact_count": 0,
            "assigned_to": "collector1"
        },
        {
            "case_id": "CASE002",
            "customer_id": "CUST002",
            "loan_id": "LOAN002",
            "loan_product": "Auto Loan",
            "principal_amount": 25000.00,
            "overdue_amount": 12500.00,
            "overdue_days": 90,
            "status": "in_progress",
            "priority": 9,
            "contact_count": 3,
            "assigned_to": "collector1"
        },
        {
            "case_id": "CASE003",
            "customer_id": "CUST003",
            "loan_id": "LOAN003",
            "loan_product": "Home Equity Loan",
            "principal_amount": 100000.00,
            "overdue_amount": 2500.00,
            "overdue_days": 15,
            "status": "contacted",
            "priority": 4,
            "contact_count": 1,
            "assigned_to": "collector2"
        },
        {
            "case_id": "CASE004",
            "customer_id": "CUST004",
            "loan_id": "LOAN004",
            "loan_product": "Credit Card",
            "principal_amount": 15000.00,
            "overdue_amount": 3500.00,
            "overdue_days": 60,
            "status": "promised_to_pay",
            "priority": 6,
            "contact_count": 2,
            "assigned_to": "collector2"
        },
        {
            "case_id": "CASE005",
            "customer_id": "CUST005",
            "loan_id": "LOAN005",
            "loan_product": "Personal Loan",
            "principal_amount": 35000.00,
            "overdue_amount": 18500.00,
            "overdue_days": 180,
            "status": "legal",
            "priority": 10,
            "contact_count": 7,
            "legal_flag": True,
            "assigned_to": "supervisor1"
        },
        {
            "case_id": "CASE006",
            "customer_id": "CUST001",
            "loan_id": "LOAN006",
            "loan_product": "Business Loan",
            "principal_amount": 75000.00,
            "overdue_amount": 8000.00,
            "overdue_days": 30,
            "status": "new",
            "priority": 5,
            "contact_count": 0,
            "assigned_to": "collector1"
        }
    ]

    created = 0
    for case_data in cases:
        # Add dates
        case_data["overdue_date"] = datetime.now() - timedelta(days=case_data["overdue_days"])
        case_data["next_action_date"] = datetime.now() + timedelta(days=3)

        case = Case(**case_data)
        db.add(case)
        created += 1

    await db.commit()
    print(f"✅ Created {created} cases")


async def main():
    """Main seed function"""
    print("🌱 Seeding database...")
    print("")

    async with AsyncSessionLocal() as db:
        try:
            await create_users(db)
            await create_customers(db)
            await create_cases(db)

            print("")
            print("✅ Database seeded successfully!")
            print("")
            print("📋 Default Credentials:")
            print("   Admin:      admin / admin123")
            print("   Supervisor: supervisor1 / admin123")
            print("   Collector:  collector1 / admin123")
            print("")

        except Exception as e:
            print(f"❌ Error seeding database: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
