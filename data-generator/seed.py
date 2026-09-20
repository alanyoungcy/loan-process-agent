"""
Data Generator - Main Seeding Script
"""
import json
import asyncio
import sys
import argparse
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'loan-agent-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from generators import CustomerGenerator, CaseGenerator, WorkflowGenerator

DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", DATABASE_URL.replace("+asyncpg", ""))


async def clear_data(engine):
    """Clear existing generated data"""
    print("🗑️  Clearing existing data...")

    async with engine.begin() as conn:
        # Delete in correct order to respect foreign keys
        await conn.execute(text("DELETE FROM genai_audit WHERE case_id IN (SELECT id FROM cases)"))
        await conn.execute(text("DELETE FROM workflow_tasks"))
        await conn.execute(text("DELETE FROM workflow_instances"))
        await conn.execute(text("DELETE FROM contact_history"))
        await conn.execute(text("DELETE FROM compliance_violations"))
        await conn.execute(text("DELETE FROM cases"))
        await conn.execute(text("DELETE FROM customers WHERE customer_id LIKE 'CUST%'"))

    print("✅ Data cleared")


async def seed_data(count: int = 200, reset: bool = False):
    """Generate and seed demo data"""
    print(f"\n{'='*60}")
    print(f"  🌱 Loan Agent Data Generator")
    print(f"{'='*60}\n")

    # Initialize generators
    customer_gen = CustomerGenerator()
    case_gen = CaseGenerator()
    workflow_gen = WorkflowGenerator()

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        if reset:
            await clear_data(engine)

        print(f"📊 Generating {count} customers and cases...")
        print()

        async with AsyncSession(engine) as session:
            customers_data = []
            cases_data = []
            workflows_data = []

            # Generate data
            for i in range(count):
                # Generate customer
                customer = customer_gen.generate_customer()
                customers_data.append(customer)

                # Generate case for customer
                case = case_gen.generate_case(
                    customer['customer_id'],
                    customer['customer_segment']
                )
                cases_data.append(case)

                # Generate workflow instance for case
                workflow = workflow_gen.generate_instance(
                    case['case_id'],
                    case
                )
                workflows_data.append(workflow)

                if (i + 1) % 50 == 0:
                    print(f"  ⏳ Generated {i + 1}/{count} records...")

            print(f"  ✅ Generated {count} records\n")

            # Insert customers
            print("💾 Inserting customers...")
            for customer in customers_data:
                await session.execute(
                    text("""
                        INSERT INTO customers (
                            customer_id, name, id_card, phone, email,
                            address, credit_score, customer_segment, created_at
                        ) VALUES (
                            :customer_id, :name, :hkid, :phone, :email,
                            :address, :credit_score, :customer_segment, NOW()
                        )
                        ON CONFLICT (customer_id) DO NOTHING
                    """),
                    {
                        'customer_id': customer['customer_id'],
                        'name': customer['name_en'],
                        'hkid': customer['hkid'],
                        'phone': customer['phone'],
                        'email': customer['email'],
                        'address': customer['address'],
                        'credit_score': customer['credit_score'],
                        'customer_segment': customer['customer_segment']
                    }
                )
            print("  ✅ Customers inserted\n")

            # Insert cases
            print("💾 Inserting cases...")
            for case in cases_data:
                await session.execute(
                    text("""
                        INSERT INTO cases (
                            case_id, customer_id, loan_id, loan_product,
                            principal_amount, overdue_amount, overdue_days,
                            status, priority, assigned_to,
                            contact_count, dispute_flag,
                            created_at, last_contact_date
                        ) VALUES (
                            :case_id, :customer_id, :loan_id, :loan_product,
                            :principal_amount, :overdue_amount, :overdue_days,
                            :status, :priority, :assigned_to,
                            :contact_count, :dispute_flag,
                            :created_at, :last_contact_date
                        )
                        ON CONFLICT (case_id) DO NOTHING
                    """),
                    case
                )
            print("  ✅ Cases inserted\n")

            # Insert workflow instances
            print("💾 Inserting workflow instances...")
            for workflow in workflows_data:
                # Get case UUID
                result = await session.execute(
                    text("SELECT id FROM cases WHERE case_id = :case_id"),
                    {'case_id': workflow['business_key']}
                )
                case_uuid = result.scalar_one_or_none()

                if case_uuid:
                    await session.execute(
                        text("""
                            INSERT INTO workflow_instances (
                                id, workflow_key, case_id, business_key,
                                status, current_task_id, current_task_name,
                                variables, started_at, completed_at, updated_at
                            ) VALUES (
                                :id, :workflow_key, :case_id,
                                :business_key, :status, :current_task_id,
                                :current_task_name, :variables,
                                :started_at, :completed_at, :updated_at
                            )
                        """),
                        {
                            'id': workflow['id'],
                            'workflow_key': workflow['workflow_key'],
                            'case_id': case_uuid,
                            'business_key': workflow['business_key'],
                            'status': workflow['status'],
                            'current_task_id': workflow['current_task_id'],
                            'current_task_name': workflow['current_task_name'],
                            'variables': json.dumps(workflow['variables']),
                            'started_at': workflow['started_at'],
                            'completed_at': workflow['completed_at'],
                            'updated_at': workflow['updated_at']
                        }
                    )
            print("  ✅ Workflow instances inserted\n")

            # Commit transaction
            await session.commit()

            print(f"{'='*60}")
            print(f"  ✅ Successfully generated {count} demo cases!")
            print(f"{'='*60}\n")

            # Print summary
            print("📊 Summary:")
            print(f"  • Customers: {len(customers_data)}")
            print(f"  • Cases: {len(cases_data)}")
            print(f"  • Workflow Instances: {len(workflows_data)}")
            print()

            # Print workflow distribution
            workflow_dist = {}
            for w in workflows_data:
                key = w['workflow_key']
                workflow_dist[key] = workflow_dist.get(key, 0) + 1

            print("🔄 Workflow Distribution:")
            for workflow_key, count in sorted(workflow_dist.items()):
                print(f"  • {workflow_key}: {count}")
            print()

    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description='Generate demo data for Loan Agent system')
    parser.add_argument('--count', type=int, default=200,
                       help='Number of cases to generate (default: 200)')
    parser.add_argument('--reset', action='store_true',
                       help='Clear existing data before generating')
    parser.add_argument('--scenario', type=str, choices=['basic', 'full', 'stress'],
                       help='Predefined scenario (basic=100, full=500, stress=10000)')

    args = parser.parse_args()

    # Handle scenarios
    if args.scenario == 'basic':
        args.count = 100
    elif args.scenario == 'full':
        args.count = 500
    elif args.scenario == 'stress':
        args.count = 10000

    # Run async seed function
    asyncio.run(seed_data(count=args.count, reset=args.reset))


if __name__ == '__main__':
    main()
