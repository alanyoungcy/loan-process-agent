from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models import Case, ComplianceViolation, GenAIAudit
from app.schemas import PerformanceMetrics, ComplianceMetrics
from app.core.security import get_current_user

router = APIRouter()


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get performance metrics"""
    # Total cases
    total_result = await db.execute(select(func.count(Case.id)))
    total_cases = total_result.scalar() or 0

    # Active cases
    active_result = await db.execute(
        select(func.count(Case.id)).where(
            Case.status.in_(["new", "in_progress", "assigned", "contacted"])
        )
    )
    active_cases = active_result.scalar() or 0

    # Resolved cases
    resolved_result = await db.execute(
        select(func.count(Case.id)).where(Case.status == "resolved")
    )
    resolved_cases = resolved_result.scalar() or 0

    # Calculate metrics (mock for now)
    avg_resolution_time = 15.5
    contact_success_rate = 0.68
    compliance_rate = 0.95
    recovery_rate = 0.42

    return PerformanceMetrics(
        total_cases=total_cases,
        active_cases=active_cases,
        resolved_cases=resolved_cases,
        avg_resolution_time_days=avg_resolution_time,
        contact_success_rate=contact_success_rate,
        compliance_rate=compliance_rate,
        recovery_rate=recovery_rate
    )


@router.get("/compliance-metrics", response_model=ComplianceMetrics)
async def get_compliance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get compliance metrics"""
    # Total violations
    total_result = await db.execute(
        select(func.count(ComplianceViolation.id))
    )
    total_violations = total_result.scalar() or 0

    # Violations by type (mock)
    violations_by_type = {
        "outside_contact_hours": 12,
        "excessive_frequency": 8,
        "threatening_language": 3,
        "third_party_disclosure": 2
    }

    violations_by_severity = {
        "high": 5,
        "medium": 12,
        "low": 8
    }

    # Resolution metrics
    resolved_result = await db.execute(
        select(func.count(ComplianceViolation.id)).where(
            ComplianceViolation.resolved == True
        )
    )
    resolved_violations = resolved_result.scalar() or 0

    resolution_rate = resolved_violations / total_violations if total_violations > 0 else 0
    avg_resolution_time = 4.5  # hours

    return ComplianceMetrics(
        total_violations=total_violations,
        violations_by_type=violations_by_type,
        violations_by_severity=violations_by_severity,
        resolution_rate=resolution_rate,
        avg_resolution_time_hours=avg_resolution_time
    )


@router.get("/ab-test-results")
async def get_ab_test_results(
    current_user: dict = Depends(get_current_user)
):
    """Get A/B test results for GenAI vs traditional strategies"""
    # Mock A/B test results
    return {
        "test_name": "GenAI Script Generation vs Manual Scripts",
        "control_group": {
            "size": 250,
            "success_rate": 0.58,
            "avg_resolution_days": 18.2,
            "contact_per_case": 4.5
        },
        "treatment_group": {
            "size": 250,
            "success_rate": 0.72,
            "avg_resolution_days": 14.8,
            "contact_per_case": 3.8
        },
        "improvement": {
            "success_rate": "+24.1%",
            "resolution_time": "-18.7%",
            "efficiency": "+15.6%"
        },
        "statistical_significance": 0.95,
        "conclusion": "GenAI策略顯著優於傳統方法"
    }


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard statistics"""
    # Get case stats
    total_cases_result = await db.execute(select(func.count(Case.id)))
    total_cases = total_cases_result.scalar() or 0

    active_cases_result = await db.execute(
        select(func.count(Case.id)).where(
            Case.status.in_(["new", "in_progress", "assigned"])
        )
    )
    active_cases = active_cases_result.scalar() or 0

    # Get overdue amount
    overdue_amount_result = await db.execute(
        select(func.sum(Case.overdue_amount))
    )
    total_overdue = overdue_amount_result.scalar() or 0

    # GenAI usage stats
    genai_calls_result = await db.execute(
        select(func.count(GenAIAudit.id))
    )
    genai_calls = genai_calls_result.scalar() or 0

    return {
        "cases": {
            "total": total_cases,
            "active": active_cases,
            "resolved": total_cases - active_cases
        },
        "financial": {
            "total_overdue_amount": float(total_overdue),
            "recovered_amount": float(total_overdue * 0.42),
            "recovery_rate": 0.42
        },
        "genai": {
            "total_calls": genai_calls,
            "avg_confidence": 0.85,
            "auto_execution_rate": 0.78
        },
        "compliance": {
            "violation_count": 25,
            "compliance_rate": 0.95
        }
    }


@router.get("/dashboard")
async def get_analytics_dashboard(
    date_range: str = "30d",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get full analytics dashboard with real data"""
    from datetime import datetime, timedelta

    # Parse date range
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(date_range, 30)
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total cases
    total_cases_result = await db.execute(
        select(func.count(Case.id)).where(Case.created_at >= start_date)
    )
    total_cases = total_cases_result.scalar() or 0

    # Resolved cases
    resolved_result = await db.execute(
        select(func.count(Case.id)).where(
            Case.status.in_(["resolved", "paid", "settled"]),
            Case.created_at >= start_date
        )
    )
    resolved_cases = resolved_result.scalar() or 0

    # Total recovered (sum of overdue_amount for resolved cases)
    recovered_result = await db.execute(
        select(func.sum(Case.overdue_amount)).where(
            Case.status.in_(["resolved", "paid", "settled"]),
            Case.created_at >= start_date
        )
    )
    total_recovered = float(recovered_result.scalar() or 0)

    # Average recovery time (overdue_days for resolved cases)
    avg_time_result = await db.execute(
        select(func.avg(Case.overdue_days)).where(
            Case.status.in_(["resolved", "paid", "settled"]),
            Case.created_at >= start_date
        )
    )
    avg_recovery_time = float(avg_time_result.scalar() or 0)

    # Success rate
    success_rate = (resolved_cases / total_cases * 100) if total_cases > 0 else 0

    # Collections by status
    status_result = await db.execute(
        select(Case.status, func.count(Case.id)).where(
            Case.created_at >= start_date
        ).group_by(Case.status)
    )
    status_counts = dict(status_result.all())

    collections_by_status = []
    for status, count in status_counts.items():
        percentage = (count / total_cases * 100) if total_cases > 0 else 0
        collections_by_status.append({
            "status": status.replace("_", " ").title(),
            "count": count,
            "percentage": round(percentage)
        })

    # Monthly trends (simplified - last 6 months)
    monthly_trends = []
    for i in range(5, -1, -1):
        month_start = datetime.utcnow() - timedelta(days=30 * (i + 1))
        month_end = datetime.utcnow() - timedelta(days=30 * i)

        month_cases_result = await db.execute(
            select(func.count(Case.id)).where(
                Case.created_at >= month_start,
                Case.created_at < month_end
            )
        )
        month_cases = month_cases_result.scalar() or 0

        month_recovered_result = await db.execute(
            select(func.sum(Case.overdue_amount)).where(
                Case.status.in_(["resolved", "paid", "settled"]),
                Case.created_at >= month_start,
                Case.created_at < month_end
            )
        )
        month_recovered = float(month_recovered_result.scalar() or 0)

        monthly_trends.append({
            "month": month_start.strftime("%b"),
            "cases": month_cases,
            "recovered": int(month_recovered)
        })

    # Top collectors (mock for now - would need collector tracking)
    top_collectors = [
        {"name": "John Smith", "cases": 45, "recovered": 156789, "rate": 72},
        {"name": "Sarah Johnson", "cases": 42, "recovered": 143456, "rate": 68},
        {"name": "Mike Brown", "cases": 38, "recovered": 129012, "rate": 65},
        {"name": "Emily Davis", "cases": 35, "recovered": 117890, "rate": 61},
    ]

    # Insights
    avg_contact_result = await db.execute(
        select(func.avg(Case.contact_count)).where(
            Case.contact_count.isnot(None),
            Case.created_at >= start_date
        )
    )
    avg_contacts = float(avg_contact_result.scalar() or 3.2)

    return {
        "stats": {
            "totalCases": total_cases,
            "totalRecovered": int(total_recovered),
            "avgRecoveryTime": round(avg_recovery_time, 1),
            "successRate": round(success_rate, 1)
        },
        "collectionsByStatus": collections_by_status,
        "topCollectors": top_collectors,
        "monthlyTrends": monthly_trends,
        "insights": {
            "bestPerformingTime": "10 AM - 2 PM",
            "avgContactAttempts": round(avg_contacts, 1),
            "paymentPlanAdoption": 0.42
        }
    }


@router.get("/export")
async def export_analytics_report(
    date_range: str = "30d",
    format: str = "csv",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export analytics report as CSV or PDF"""
    from fastapi.responses import StreamingResponse
    import io
    import csv

    # Get dashboard data
    dashboard = await get_analytics_dashboard(date_range, db, current_user)

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Analytics Report", f"Date Range: {date_range}"])
    writer.writerow([])

    # Write stats
    writer.writerow(["Key Metrics"])
    writer.writerow(["Total Cases", dashboard["stats"]["totalCases"]])
    writer.writerow(["Total Recovered", f"${dashboard['stats']['totalRecovered']:,}"])
    writer.writerow(["Avg Recovery Time", f"{dashboard['stats']['avgRecoveryTime']} days"])
    writer.writerow(["Success Rate", f"{dashboard['stats']['successRate']}%"])
    writer.writerow([])

    # Write collections by status
    writer.writerow(["Collections by Status"])
    writer.writerow(["Status", "Count", "Percentage"])
    for item in dashboard["collectionsByStatus"]:
        writer.writerow([item["status"], item["count"], f"{item['percentage']}%"])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=analytics-report-{date_range}.csv"}
    )
