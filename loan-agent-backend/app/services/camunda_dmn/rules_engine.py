"""
Business Rules Engine for Loan Collection
Python-based rules engine inspired by Drools architecture
"""
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RulePriority(Enum):
    """Rule execution priority"""
    HIGHEST = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    LOWEST = 5


@dataclass
class RuleResult:
    """Result of a rule execution"""
    rule_name: str
    executed: bool
    actions_taken: List[str] = field(default_factory=list)
    modifications: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Rule:
    """Business rule definition"""
    name: str
    description: str
    priority: RulePriority
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], RuleResult]
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


class RulesEngine:
    """
    Business Rules Engine for loan collection

    Manages and executes business rules against case facts
    """

    def __init__(self):
        self.rules: List[Rule] = []
        self.execution_history: List[RuleResult] = []

    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)
        logger.info(f"Rule added: {rule.name}")

    def remove_rule(self, rule_name: str):
        """Remove a rule by name"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"Rule removed: {rule_name}")

    def enable_rule(self, rule_name: str):
        """Enable a rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Rule enabled: {rule_name}")
                break

    def disable_rule(self, rule_name: str):
        """Disable a rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Rule disabled: {rule_name}")
                break

    def execute(self, facts: Dict[str, Any]) -> List[RuleResult]:
        """
        Execute all applicable rules against the provided facts

        Args:
            facts: Dictionary containing case data and context

        Returns:
            List of RuleResult objects
        """
        results = []

        # Sort rules by priority
        sorted_rules = sorted(
            [r for r in self.rules if r.enabled],
            key=lambda x: x.priority.value
        )

        logger.info(f"Executing {len(sorted_rules)} rules against facts")

        for rule in sorted_rules:
            try:
                # Check condition
                if rule.condition(facts):
                    logger.info(f"Rule condition met: {rule.name}")

                    # Execute action
                    result = rule.action(facts)
                    result.rule_name = rule.name
                    result.executed = True

                    results.append(result)
                    self.execution_history.append(result)

                    logger.info(
                        f"Rule executed: {rule.name}, "
                        f"Actions: {len(result.actions_taken)}, "
                        f"Modifications: {len(result.modifications)}"
                    )
                else:
                    logger.debug(f"Rule condition not met: {rule.name}")

            except Exception as e:
                logger.error(f"Error executing rule {rule.name}: {str(e)}")
                results.append(RuleResult(
                    rule_name=rule.name,
                    executed=False,
                    actions_taken=[f"Error: {str(e)}"]
                ))

        return results

    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """Get all rules with a specific tag"""
        return [r for r in self.rules if tag in r.tags]

    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        logger.info("Execution history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_executions = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.executed)

        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules if r.enabled),
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": total_executions - successful,
        }


# Global rules engine instance
rules_engine = RulesEngine()
