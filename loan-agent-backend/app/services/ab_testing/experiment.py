"""
A/B Testing Service
Manages experiments, assignments, and statistical analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from uuid import UUID
import scipy.stats as stats

from app.models.additional import ABTestExperiment, ABTestAssignment
from app.models.case import Case

logger = logging.getLogger(__name__)


class ABTestService:
    """Service for managing A/B tests in collection strategies"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experiment(
        self,
        name: str,
        description: str,
        control_description: str,
        treatment_description: str,
        hypothesis: str,
        target_metric: str,
        target_sample_size: int,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        created_by: str = None
    ) -> ABTestExperiment:
        """
        Create a new A/B test experiment

        Args:
            name: Experiment name (unique identifier)
            description: What is being tested
            control_description: Description of control variant
            treatment_description: Description of treatment variant
            hypothesis: What you expect to happen
            target_metric: Metric to measure (payment_rate, contact_success, etc.)
            target_sample_size: Desired sample size per variant
            start_date: When experiment starts
            end_date: When experiment ends (optional)
            created_by: User creating the experiment

        Returns:
            Created experiment
        """
        experiment = ABTestExperiment(
            name=name,
            description=description,
            control_description=control_description,
            treatment_description=treatment_description,
            hypothesis=hypothesis,
            target_metric=target_metric,
            target_sample_size=target_sample_size,
            start_date=start_date,
            end_date=end_date,
            status="active",
            created_by=created_by
        )

        self.db.add(experiment)
        await self.db.commit()
        await self.db.refresh(experiment)

        logger.info(f"Created A/B test experiment: {name}")

        return experiment

    async def assign_variant(
        self,
        experiment_name: str,
        case_id: UUID
    ) -> str:
        """
        Assign a case to control or treatment variant
        Uses consistent hashing for stable assignments

        Args:
            experiment_name: Name of experiment
            case_id: Case ID to assign

        Returns:
            Variant name ("control" or "treatment")
        """
        # Check if already assigned
        result = await self.db.execute(
            select(ABTestAssignment).where(
                ABTestAssignment.experiment_name == experiment_name,
                ABTestAssignment.case_id == case_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"Case {case_id} already assigned to {existing.variant}")
            return existing.variant

        # Use consistent hashing for 50/50 split
        hash_input = f"{case_id}{experiment_name}".encode()
        hash_value = hashlib.md5(hash_input).hexdigest()
        variant = "treatment" if int(hash_value, 16) % 2 == 0 else "control"

        # Create assignment
        assignment = ABTestAssignment(
            experiment_name=experiment_name,
            case_id=case_id,
            variant=variant,
            assigned_at=datetime.utcnow()
        )

        self.db.add(assignment)
        await self.db.commit()

        logger.info(f"Assigned case {case_id} to {variant} in {experiment_name}")

        return variant

    async def track_outcome(
        self,
        experiment_name: str,
        case_id: UUID,
        outcome_data: Dict[str, Any],
        success: bool
    ) -> None:
        """
        Track outcome for an assigned case

        Args:
            experiment_name: Name of experiment
            case_id: Case ID
            outcome_data: Outcome metrics (payment amount, contact success, etc.)
            success: Whether the outcome was successful
        """
        # Update assignment
        await self.db.execute(
            update(ABTestAssignment)
            .where(
                ABTestAssignment.experiment_name == experiment_name,
                ABTestAssignment.case_id == case_id
            )
            .values(
                outcome_data=outcome_data,
                completed_at=datetime.utcnow(),
                success=success
            )
        )

        # Update experiment counts
        result = await self.db.execute(
            select(ABTestAssignment).where(
                ABTestAssignment.experiment_name == experiment_name,
                ABTestAssignment.case_id == case_id
            )
        )
        assignment = result.scalar_one_or_none()

        if assignment:
            variant_field = (
                "control" if assignment.variant == "control" else "treatment"
            )

            # Increment total count
            await self.db.execute(
                update(ABTestExperiment)
                .where(ABTestExperiment.name == experiment_name)
                .values({
                    f"{variant_field}_total_count":
                        getattr(ABTestExperiment, f"{variant_field}_total_count") + 1
                })
            )

            # Increment success count if successful
            if success:
                await self.db.execute(
                    update(ABTestExperiment)
                    .where(ABTestExperiment.name == experiment_name)
                    .values({
                        f"{variant_field}_success_count":
                            getattr(ABTestExperiment, f"{variant_field}_success_count") + 1
                    })
                )

        await self.db.commit()

        logger.info(
            f"Tracked outcome for case {case_id} in {experiment_name}: success={success}"
        )

    async def get_experiment_results(
        self,
        experiment_name: str
    ) -> Dict[str, Any]:
        """
        Get current results and statistical analysis for experiment

        Args:
            experiment_name: Name of experiment

        Returns:
            Results dict with statistics
        """
        result = await self.db.execute(
            select(ABTestExperiment).where(
                ABTestExperiment.name == experiment_name
            )
        )
        experiment = result.scalar_one_or_none()

        if not experiment:
            raise ValueError(f"Experiment {experiment_name} not found")

        # Calculate conversion rates
        control_rate = (
            experiment.control_success_count / experiment.control_total_count
            if experiment.control_total_count > 0 else 0
        )
        treatment_rate = (
            experiment.treatment_success_count / experiment.treatment_total_count
            if experiment.treatment_total_count > 0 else 0
        )

        # Calculate statistical significance (Chi-square test)
        if (experiment.control_total_count >= 30 and
            experiment.treatment_total_count >= 30):

            # Observed frequencies
            observed = [
                [experiment.control_success_count,
                 experiment.control_total_count - experiment.control_success_count],
                [experiment.treatment_success_count,
                 experiment.treatment_total_count - experiment.treatment_success_count]
            ]

            chi2, p_value, dof, expected = stats.chi2_contingency(observed)

            # Determine winner (if p < 0.05, statistically significant)
            if p_value < 0.05:
                if treatment_rate > control_rate:
                    winner = "treatment"
                elif control_rate > treatment_rate:
                    winner = "control"
                else:
                    winner = "inconclusive"
            else:
                winner = "inconclusive"

            # Update experiment
            experiment.statistical_significance = p_value
            experiment.winner = winner
            await self.db.commit()

        else:
            p_value = None
            winner = "insufficient_data"

        # Calculate confidence intervals (95%)
        control_ci = self._calculate_confidence_interval(
            experiment.control_success_count,
            experiment.control_total_count
        )
        treatment_ci = self._calculate_confidence_interval(
            experiment.treatment_success_count,
            experiment.treatment_total_count
        )

        # Calculate lift
        lift = (
            ((treatment_rate - control_rate) / control_rate * 100)
            if control_rate > 0 else 0
        )

        return {
            "experiment_name": experiment_name,
            "status": experiment.status,
            "start_date": experiment.start_date.isoformat(),
            "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
            "control": {
                "total": experiment.control_total_count,
                "successes": experiment.control_success_count,
                "conversion_rate": control_rate,
                "confidence_interval": control_ci
            },
            "treatment": {
                "total": experiment.treatment_total_count,
                "successes": experiment.treatment_success_count,
                "conversion_rate": treatment_rate,
                "confidence_interval": treatment_ci
            },
            "statistics": {
                "lift_percentage": lift,
                "p_value": p_value,
                "is_significant": p_value < 0.05 if p_value else False,
                "winner": winner
            },
            "target_sample_size": experiment.target_sample_size,
            "sample_size_reached": (
                experiment.control_total_count >= experiment.target_sample_size and
                experiment.treatment_total_count >= experiment.target_sample_size
            )
        }

    def _calculate_confidence_interval(
        self,
        successes: int,
        total: int,
        confidence: float = 0.95
    ) -> tuple:
        """
        Calculate confidence interval for conversion rate

        Args:
            successes: Number of successes
            total: Total trials
            confidence: Confidence level (default 0.95 for 95%)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if total == 0:
            return (0, 0)

        p = successes / total
        z = stats.norm.ppf((1 + confidence) / 2)
        margin = z * ((p * (1 - p) / total) ** 0.5)

        lower = max(0, p - margin)
        upper = min(1, p + margin)

        return (lower, upper)

    async def stop_experiment(
        self,
        experiment_name: str,
        reason: str = None
    ) -> None:
        """
        Stop an active experiment

        Args:
            experiment_name: Name of experiment
            reason: Reason for stopping
        """
        await self.db.execute(
            update(ABTestExperiment)
            .where(ABTestExperiment.name == experiment_name)
            .values(
                status="completed",
                end_date=datetime.utcnow()
            )
        )
        await self.db.commit()

        logger.info(f"Stopped experiment {experiment_name}: {reason}")

    async def list_active_experiments(self) -> List[ABTestExperiment]:
        """
        List all active experiments

        Returns:
            List of active experiments
        """
        result = await self.db.execute(
            select(ABTestExperiment).where(
                ABTestExperiment.status == "active"
            )
        )
        return result.scalars().all()

    async def get_case_assignments(
        self,
        case_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get all experiment assignments for a case

        Args:
            case_id: Case ID

        Returns:
            List of assignments
        """
        result = await self.db.execute(
            select(ABTestAssignment).where(
                ABTestAssignment.case_id == case_id
            )
        )
        assignments = result.scalars().all()

        return [
            {
                "experiment_name": a.experiment_name,
                "variant": a.variant,
                "assigned_at": a.assigned_at.isoformat(),
                "completed": a.completed_at is not None,
                "success": a.success
            }
            for a in assignments
        ]
