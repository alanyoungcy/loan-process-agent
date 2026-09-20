"""
Rules Service - Integration between rules engine and case management
"""
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.camunda_dmn.rules_engine import rules_engine, RuleResult
from app.rules.collection_rules import initialize_rules
from app.models import Case
import logging

logger = logging.getLogger(__name__)


class RulesService:
    """Service for applying business rules to cases"""

    def __init__(self):
        """Initialize rules service"""
        # Initialize rules on first use
        if len(rules_engine.rules) == 0:
            initialize_rules()

    def case_to_facts(self, case: Case, additional_facts: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert a Case object to facts dictionary for rules engine

        Args:
            case: Case object
            additional_facts: Additional facts to include

        Returns:
            Dictionary of facts
        """
        facts = {
            "case_id": case.case_id,
            "customer_id": case.customer_id,
            "loan_id": case.loan_id,
            "principal_amount": float(case.principal_amount),
            "overdue_amount": float(case.overdue_amount),
            "overdue_days": case.overdue_days,
            "status": case.status,
            "priority": case.priority,
            "contact_count": case.contact_count,
            "dispute_flag": case.dispute_flag,
            "legal_flag": case.legal_flag,
            "current_time": datetime.now(),
        }

        # Add optional fields
        if case.last_contact_date:
            facts["last_contact_date"] = case.last_contact_date.isoformat()

        if case.next_action_date:
            facts["next_action_date"] = case.next_action_date.isoformat()

        if case.tags:
            facts["tags"] = case.tags

        # Merge additional facts
        if additional_facts:
            facts.update(additional_facts)

        return facts

    async def evaluate_case(
        self,
        case: Case,
        additional_facts: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a case against all business rules

        Args:
            case: Case to evaluate
            additional_facts: Additional context

        Returns:
            Dictionary containing:
                - rules_executed: List of rule names executed
                - modifications: Suggested modifications to case
                - recommendations: List of recommendations
                - can_contact: Whether contact is allowed
        """
        # Convert case to facts
        facts = self.case_to_facts(case, additional_facts)

        # Execute rules
        results = rules_engine.execute(facts)

        # Aggregate results
        aggregated = self._aggregate_results(results)

        logger.info(
            f"Evaluated case {case.case_id}: "
            f"{len(results)} rules executed, "
            f"{len(aggregated['modifications'])} modifications suggested"
        )

        return aggregated

    async def apply_rules_to_case(
        self,
        case: Case,
        db: AsyncSession,
        additional_facts: Dict[str, Any] = None,
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate rules and optionally apply modifications to case

        Args:
            case: Case to evaluate
            db: Database session
            additional_facts: Additional context
            auto_apply: Whether to automatically apply modifications

        Returns:
            Evaluation results with applied flag
        """
        # Evaluate case
        evaluation = await self.evaluate_case(case, additional_facts)

        # Apply modifications if requested
        if auto_apply and evaluation["modifications"]:
            for key, value in evaluation["modifications"].items():
                if hasattr(case, key):
                    setattr(case, key, value)
                    logger.info(f"Applied modification: {key} = {value}")

            case.updated_at = datetime.now()
            await db.commit()
            await db.refresh(case)

            evaluation["applied"] = True
        else:
            evaluation["applied"] = False

        return evaluation

    def _aggregate_results(self, results: List[RuleResult]) -> Dict[str, Any]:
        """
        Aggregate multiple rule results into a single response

        Args:
            results: List of RuleResult objects

        Returns:
            Aggregated results dictionary
        """
        aggregated = {
            "rules_executed": [],
            "actions_taken": [],
            "modifications": {},
            "recommendations": [],
            "can_contact": True,  # Default to true
        }

        for result in results:
            if result.executed:
                aggregated["rules_executed"].append(result.rule_name)
                aggregated["actions_taken"].extend(result.actions_taken)
                aggregated["recommendations"].extend(result.recommendations)

                # Merge modifications
                for key, value in result.modifications.items():
                    # Special handling for can_contact - if any rule says false, it's false
                    if key == "can_contact" and not value:
                        aggregated["can_contact"] = False
                    # For priority, take the highest
                    elif key == "priority":
                        aggregated["modifications"][key] = max(
                            aggregated["modifications"].get(key, 0),
                            value
                        )
                    else:
                        aggregated["modifications"][key] = value

        # Deduplicate recommendations
        aggregated["recommendations"] = list(set(aggregated["recommendations"]))

        return aggregated

    def get_rules_by_category(self, category: str) -> List[str]:
        """
        Get all rules for a specific category

        Args:
            category: Rule category/tag

        Returns:
            List of rule names
        """
        rules = rules_engine.get_rules_by_tag(category)
        return [r.name for r in rules]

    def get_all_rules(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered rules

        Returns:
            List of rule information dictionaries
        """
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "priority": rule.priority.name,
                "enabled": rule.enabled,
                "tags": rule.tags,
            }
            for rule in rules_engine.rules
        ]

    def enable_rule(self, rule_name: str):
        """Enable a specific rule"""
        rules_engine.enable_rule(rule_name)

    def disable_rule(self, rule_name: str):
        """Disable a specific rule"""
        rules_engine.disable_rule(rule_name)

    def get_statistics(self) -> Dict[str, Any]:
        """Get rules engine execution statistics"""
        return rules_engine.get_statistics()


# Global rules service instance
rules_service = RulesService()
