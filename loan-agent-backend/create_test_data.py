"""Create test data for the system"""
import asyncio
import uuid
import os
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import User, Case, Customer
from app.core.security import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL", "")


async def create_test_data():
    """Create test users and cases"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test users
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            role="admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
        )
        session.add(admin)

        collector = User(
            username="collector1",
            email="collector1@example.com",
            full_name="Collector One",
            role="collector",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
        )
        session.add(collector)

        await session.commit()
        await session.refresh(admin)
        await session.refresh(collector)

        print(f"✅ Created users: {admin.username}, {collector.username}")

        # Create test customer
        customer_id = f"CUST{uuid.uuid4().hex[:8].upper()}"
        customer = Customer(
            customer_id=customer_id,
            name="John Doe",
            phone="+1234567890",
            email="john.doe@example.com",
            id_number="ID123456789",
            address="123 Main St, City, Country",
        )
        session.add(customer)
        await session.commit()
        await session.refresh(customer)

        print(f"✅ Created customer: {customer.customer_id}")

        # Create test case
        case_id = f"CASE{uuid.uuid4().hex[:8].upper()}"
        loan_id = f"LOAN{uuid.uuid4().hex[:8].upper()}"

        test_case = Case(
            case_id=case_id,
            customer_id=customer.id,
            loan_id=loan_id,
            loan_product="Personal Loan",
            principal_amount=Decimal("50000.00"),
            overdue_amount=Decimal("5000.00"),
            overdue_days=45,
            overdue_date=datetime.now() - timedelta(days=45),
            status="new",
            priority=7,
            contact_count=0,
            dispute_flag=False,
            tags=["high_priority", "first_contact"],
        )
        session.add(test_case)
        await session.commit()
        await session.refresh(test_case)

        print(f"✅ Created case: {test_case.case_id} (ID: {test_case.id})")
        print(f"   Customer: {customer.name}")
        print(f"   Overdue: ${test_case.overdue_amount} ({test_case.overdue_days} days)")

    await engine.dispose()
    return test_case.id


if __name__ == "__main__":
    case_id = asyncio.run(create_test_data())
    print(f"\n🎉 Test data created successfully!")
    print(f"\nTest case ID: {case_id}")
    print(f"\nLogin credentials:")
    print(f"  Admin: admin / admin123")
    print(f"  Collector: collector1 / admin123")
