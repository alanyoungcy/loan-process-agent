"""
Advanced Analytics Service
Provides sophisticated analytics: cohort analysis, strategy effectiveness, predictive modeling
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
import pandas as pd
import numpy as np

from app.models.case import Case
from app.models.additional import ABTestAssignment, ContactHistory, ComplianceViolation

logger = logging.getLogger(__name__)


class AdvancedAnalyticsService:
    """Service for advanced analytics and insights"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def cohort_analysis(
        self,
        cohort_by: str = "month",  # month, overdue_days, amount_range
        metric: str = "payment_rate",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Perform cohort analysis to track case outcomes over time

        Args:
            cohort_by: How to group cohorts (month, overdue_days, amount_range)
            metric: Metric to track (payment_rate, resolution_time, contact_success)
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Cohort analysis results with trends
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=365)
        if not end_date:
            end_date = datetime.utcnow()

        # Fetch cases
        query = select(Case).where(
            and_(
                Case.created_at >= start_date,
                Case.created_at <= end_date
            )
        )
        result = await self.db.execute(query)
        cases = result.scalars().all()

        # Convert to pandas for analysis
        df = pd.DataFrame([{
            'id': str(c.id),
            'created_at': c.created_at,
            'overdue_amount': float(c.overdue_amount),
            'overdue_days': c.overdue_days,
            'status': c.status,
            'priority': c.priority
        } for c in cases])

        if df.empty:
            return {"cohorts": [], "message": "No data for selected period"}

        # Create cohorts based on grouping
        if cohort_by == "month":
            df['cohort'] = pd.to_datetime(df['created_at']).dt.to_period('M').astype(str)
        elif cohort_by == "overdue_days":
            df['cohort'] = pd.cut(
                df['overdue_days'],
                bins=[0, 30, 60, 90, 180, 365, float('inf')],
                labels=['0-30d', '31-60d', '61-90d', '91-180d', '181-365d', '365d+']
            )
        elif cohort_by == "amount_range":
            df['cohort'] = pd.cut(
                df['overdue_amount'],
                bins=[0, 10000, 50000, 100000, 500000, float('inf')],
                labels=['<10K', '10K-50K', '50K-100K', '100K-500K', '500K+']
            )

        # Calculate metric for each cohort
        cohorts = []
        for cohort_name, group in df.groupby('cohort'):
            cohort_data = {
                'cohort': str(cohort_name),
                'size': len(group),
                'avg_overdue_amount': float(group['overdue_amount'].mean()),
                'avg_overdue_days': float(group['overdue_days'].mean())
            }

            # Calculate metric
            if metric == "payment_rate":
                paid_count = len(group[group['status'].isin(['paid', 'settled'])])
                cohort_data['metric_value'] = paid_count / len(group) if len(group) > 0 else 0
                cohort_data['metric_name'] = 'Payment Rate'

            elif metric == "resolution_time":
                resolved = group[group['status'].isin(['paid', 'settled', 'closed'])]
                cohort_data['metric_value'] = float(resolved['overdue_days'].mean()) if len(resolved) > 0 else 0
                cohort_data['metric_name'] = 'Avg Resolution Days'

            cohorts.append(cohort_data)

        # Sort cohorts
        cohorts.sort(key=lambda x: x['cohort'])

        return {
            'cohorts': cohorts,
            'cohort_by': cohort_by,
            'metric': metric,
            'period': f"{start_date.date()} to {end_date.date()}",
            'total_cases': len(df)
        }

    async def strategy_effectiveness(
        self,
        strategy: Optional[str] = None,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze effectiveness of collection strategies

        Args:
            strategy: Specific strategy to analyze (None for all)
            period_days: Analysis period in days

        Returns:
            Strategy effectiveness metrics
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Fetch cases with strategies
        query = select(Case).where(Case.created_at >= start_date)
        if strategy:
            query = query.where(Case.recommended_strategy == strategy)

        result = await self.db.execute(query)
        cases = result.scalars().all()

        # Group by strategy
        strategy_stats = {}
        for case in cases:
            strat = case.recommended_strategy or 'no_strategy'

            if strat not in strategy_stats:
                strategy_stats[strat] = {
                    'total_cases': 0,
                    'paid_count': 0,
                    'total_amount': 0,
                    'collected_amount': 0,
                    'avg_resolution_days': [],
                    'contact_counts': []
                }

            stats = strategy_stats[strat]
            stats['total_cases'] += 1
            stats['total_amount'] += float(case.overdue_amount)

            if case.status in ['paid', 'settled']:
                stats['paid_count'] += 1
                stats['collected_amount'] += float(case.overdue_amount)
                if case.overdue_days:
                    stats['avg_resolution_days'].append(case.overdue_days)

            if case.contact_count:
                stats['contact_counts'].append(case.contact_count)

        # Calculate metrics
        results = []
        for strat, stats in strategy_stats.items():
            payment_rate = stats['paid_count'] / stats['total_cases'] if stats['total_cases'] > 0 else 0
            collection_rate = stats['collected_amount'] / stats['total_amount'] if stats['total_amount'] > 0 else 0

            results.append({
                'strategy': strat,
                'total_cases': stats['total_cases'],
                'payment_rate': payment_rate,
                'collection_rate': collection_rate,
                'avg_resolution_days': np.mean(stats['avg_resolution_days']) if stats['avg_resolution_days'] else 0,
                'avg_contacts': np.mean(stats['contact_counts']) if stats['contact_counts'] else 0,
                'total_collected': stats['collected_amount']
            })

        # Sort by payment rate
        results.sort(key=lambda x: x['payment_rate'], reverse=True)

        return {
            'strategies': results,
            'period_days': period_days,
            'analysis_date': datetime.utcnow().isoformat()
        }

    async def predictive_default_risk(
        self,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Predict default risk using simple scoring model

        Args:
            case_id: Case ID to analyze

        Returns:
            Risk score and factors
        """
        result = await self.db.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()

        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Simple risk scoring model
        risk_score = 0.0
        risk_factors = []

        # Overdue days factor (0-40 points)
        if case.overdue_days > 180:
            risk_score += 40
            risk_factors.append("Long overdue (180+ days)")
        elif case.overdue_days > 90:
            risk_score += 30
            risk_factors.append("Very overdue (90+ days)")
        elif case.overdue_days > 30:
            risk_score += 15
            risk_factors.append("Overdue (30+ days)")

        # Amount factor (0-30 points)
        amount = float(case.overdue_amount)
        if amount > 100000:
            risk_score += 30
            risk_factors.append("High amount (>100K)")
        elif amount > 50000:
            risk_score += 20
            risk_factors.append("Medium-high amount (>50K)")
        elif amount > 10000:
            risk_score += 10
            risk_factors.append("Medium amount (>10K)")

        # Contact response factor (0-20 points)
        if case.contact_count and case.contact_count > 5:
            risk_score += 20
            risk_factors.append("Multiple unsuccessful contacts")
        elif case.contact_count and case.contact_count > 2:
            risk_score += 10
            risk_factors.append("Several contact attempts")

        # Dispute flag (0-10 points)
        if case.dispute_flag:
            risk_score += 10
            risk_factors.append("Active dispute")

        # Priority factor (already high priority = higher risk)
        if case.priority >= 8:
            risk_score += 10
            risk_factors.append("Already high priority")

        # Normalize to 0-100
        risk_score = min(100, risk_score)

        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            'case_id': str(case.id),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': self._get_risk_recommendation(risk_score),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def _get_risk_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score"""
        if risk_score >= 70:
            return "Immediate escalation to legal team recommended"
        elif risk_score >= 50:
            return "Assign to senior collector with settlement authority"
        elif risk_score >= 30:
            return "Increase contact frequency and offer payment plan"
        else:
            return "Standard collection process"

    async def compliance_dashboard(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate compliance dashboard metrics

        Args:
            period_days: Analysis period

        Returns:
            Compliance metrics and trends
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Fetch violations
        query = select(ComplianceViolation).where(
            ComplianceViolation.detected_at >= start_date
        )
        result = await self.db.execute(query)
        violations = result.scalars().all()

        # Analyze violations
        violation_by_type = {}
        violation_by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        violations_over_time = {}

        for v in violations:
            # By type
            vtype = v.violation_type
            if vtype not in violation_by_type:
                violation_by_type[vtype] = 0
            violation_by_type[vtype] += 1

            # By severity
            if v.severity in violation_by_severity:
                violation_by_severity[v.severity] += 1

            # Over time (by day)
            day = v.detected_at.date().isoformat()
            if day not in violations_over_time:
                violations_over_time[day] = 0
            violations_over_time[day] += 1

        # Calculate resolution rate
        resolved_count = sum(1 for v in violations if v.resolved)
        resolution_rate = resolved_count / len(violations) if violations else 0

        # Top violation types
        top_violations = sorted(
            [{"type": k, "count": v} for k, v in violation_by_type.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]

        return {
            'period_days': period_days,
            'total_violations': len(violations),
            'resolved_violations': resolved_count,
            'resolution_rate': resolution_rate,
            'by_severity': violation_by_severity,
            'top_violations': top_violations,
            'violations_over_time': [
                {"date": k, "count": v}
                for k, v in sorted(violations_over_time.items())
            ],
            'critical_violations': [
                {
                    'id': str(v.id),
                    'type': v.violation_type,
                    'case_id': str(v.case_id) if v.case_id else None,
                    'detected_at': v.detected_at.isoformat(),
                    'resolved': v.resolved
                }
                for v in violations if v.severity == "critical" and not v.resolved
            ]
        }

    async def collection_funnel_analysis(
        self,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze collection funnel: contact → response → payment

        Args:
            period_days: Analysis period

        Returns:
            Funnel metrics with conversion rates
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Fetch cases
        query = select(Case).where(Case.created_at >= start_date)
        result = await self.db.execute(query)
        cases = result.scalars().all()

        total_cases = len(cases)
        contacted_cases = sum(1 for c in cases if c.contact_count and c.contact_count > 0)
        responded_cases = sum(1 for c in cases if c.last_contact_date is not None)
        paid_cases = sum(1 for c in cases if c.status in ['paid', 'settled'])

        return {
            'period_days': period_days,
            'funnel': [
                {
                    'stage': 'Total Cases',
                    'count': total_cases,
                    'conversion_rate': 1.0
                },
                {
                    'stage': 'Contacted',
                    'count': contacted_cases,
                    'conversion_rate': contacted_cases / total_cases if total_cases > 0 else 0
                },
                {
                    'stage': 'Responded',
                    'count': responded_cases,
                    'conversion_rate': responded_cases / contacted_cases if contacted_cases > 0 else 0
                },
                {
                    'stage': 'Paid',
                    'count': paid_cases,
                    'conversion_rate': paid_cases / responded_cases if responded_cases > 0 else 0
                }
            ],
            'overall_conversion': paid_cases / total_cases if total_cases > 0 else 0
        }


# Factory function
def get_analytics_service(db: AsyncSession) -> AdvancedAnalyticsService:
    """Get analytics service instance"""
    return AdvancedAnalyticsService(db)
