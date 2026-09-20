"""Test rules engine"""
import pytest
from app.services.drools.rules_engine import Rule, RulePriority, RuleResult, RulesEngine


def test_rules_engine_initialization():
    """Test rules engine can be initialized"""
    engine = RulesEngine()
    assert engine is not None
    assert len(engine.rules) == 0


def test_add_rule():
    """Test adding a rule"""
    engine = RulesEngine()
    
    rule = Rule(
        name="Test Rule",
        description="Test rule description",
        priority=RulePriority.NORMAL,
        condition=lambda facts: facts.get("test") == True,
        action=lambda facts: RuleResult(rule_name="Test", executed=True)
    )
    
    engine.add_rule(rule)
    assert len(engine.rules) == 1


def test_rule_execution():
    """Test rule execution"""
    engine = RulesEngine()
    
    def condition(facts):
        return facts.get("amount") > 1000
    
    def action(facts):
        result = RuleResult(rule_name="High Amount", executed=True)
        result.modifications["priority"] = 10
        return result
    
    rule = Rule(
        name="High Amount Rule",
        description="Increase priority for high amounts",
        priority=RulePriority.HIGH,
        condition=condition,
        action=action
    )
    
    engine.add_rule(rule)
    
    # Test with matching facts
    facts = {"amount": 5000}
    results = engine.execute(facts)
    
    assert len(results) == 1
    assert results[0].executed
    assert results[0].modifications["priority"] == 10
