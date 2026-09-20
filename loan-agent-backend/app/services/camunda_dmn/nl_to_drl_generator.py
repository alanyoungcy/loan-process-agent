"""
Natural Language to DRL Generator Service
Converts natural language rule descriptions to Drools DRL syntax
Uses LLM with few-shot prompting and DRL syntax validation
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.genai.llm_client import get_llm_client
from app.services.genai.rag_service import get_rag_service

logger = logging.getLogger(__name__)


class NLToDRLGenerator:
    """
    Service to convert natural language rule descriptions to Drools DRL
    """

    def __init__(self):
        self.llm_client = get_llm_client()
        self.rag_service = get_rag_service()

    async def generate_drl_from_nl(
        self,
        natural_language: str,
        rule_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate DRL rule from natural language description

        Args:
            natural_language: Rule description in plain English/Chinese
            rule_name: Optional rule name (auto-generated if not provided)
            context: Optional context (domain objects, available fields, etc.)

        Returns:
            Dict with DRL content, confidence, validation results
        """
        # Retrieve similar existing rules for context
        similar_rules_context = await self._get_similar_rules_context(natural_language)

        # Build system prompt with DRL syntax examples
        system_prompt = self._build_drl_system_prompt(similar_rules_context)

        # Build user prompt
        user_prompt = self._build_user_prompt(natural_language, rule_name, context)

        try:
            # Generate DRL using LLM
            drl_response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for code generation
                max_tokens=1000
            )

            drl_content = drl_response["content"]

            # Extract DRL from response (in case LLM adds explanation)
            drl_content = self._extract_drl(drl_content)

            # Validate DRL syntax
            validation = self._validate_drl_syntax(drl_content)

            # Calculate confidence
            confidence = self._calculate_confidence(
                drl_content,
                validation,
                similar_rules_context
            )

            return {
                "drl_content": drl_content,
                "confidence": confidence,
                "validation": validation,
                "rule_name": self._extract_rule_name(drl_content) or rule_name,
                "natural_language": natural_language,
                "requires_review": confidence < 0.75 or not validation["valid"]
            }

        except Exception as e:
            logger.error(f"Failed to generate DRL: {str(e)}")
            raise

    async def _get_similar_rules_context(self, description: str) -> str:
        """Retrieve similar existing DRL rules for context"""
        # In production, this would query a collection of existing rules
        # For now, return example templates
        return """
Example 1: Priority Rule
rule "High Value Overdue Priority"
    when
        $case : Case(overdueAmount > 100000, overdueDays > 30)
    then
        $case.setPriority(9);
        $case.addTag("high_value");
        update($case);
end

Example 2: Strategy Assignment
rule "SMS Strategy for Early Stage"
    when
        $case : Case(overdueDays < 30, overdueAmount < 10000)
    then
        $case.setRecommendedStrategy("sms_reminder");
        update($case);
end

Example 3: Compliance Check
rule "Block Third Party Contact"
    when
        $action : ContactAction(contactType == "third_party", customerConsent == false)
    then
        $action.setBlocked(true);
        $action.setViolationType("third_party_disclosure");
        update($action);
end
"""

    def _build_drl_system_prompt(self, examples: str) -> str:
        """Build system prompt with DRL syntax guidance"""
        return f"""You are an expert in Drools Rule Language (DRL) syntax.
Your task is to convert natural language rule descriptions into valid DRL rules.

DRL SYNTAX RULES:
1. Rule structure: rule "Name" when <conditions> then <actions> end
2. Conditions use pattern matching: ClassName(field operator value, ...)
3. Variables start with $: $variable : ClassName(...)
4. Actions: modify($var), update($var), insert(new Object())
5. Operators: ==, !=, <, >, <=, >=, matches
6. Logical: &&, ||, not
7. Must call update() after modifying facts

DOMAIN OBJECTS AVAILABLE:
- Case: id, caseId, customerId, overdueAmount, overdueDays, priority, status, tags, recommendedStrategy
- Customer: id, customerId, segment, riskLevel, creditScore
- ContactAction: id, contactType, contactTime, blocked, violationType

EXAMPLE RULES:
{examples}

OUTPUT FORMAT:
- Generate ONLY the DRL rule code
- Include proper indentation
- Use clear, descriptive rule names
- Add comments if logic is complex
- Ensure all variables are properly bound
"""

    def _build_user_prompt(
        self,
        natural_language: str,
        rule_name: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt with the rule description"""
        prompt = f"Convert this rule description to DRL:\n\n{natural_language}\n\n"

        if rule_name:
            prompt += f"Rule name: {rule_name}\n\n"

        if context:
            prompt += f"Additional context: {context}\n\n"

        prompt += "Generate the DRL rule:"

        return prompt

    def _extract_drl(self, response: str) -> str:
        """Extract DRL code from LLM response"""
        # Look for rule "..." when ... then ... end pattern
        match = re.search(r'rule\s+"[^"]+"\s+when.*?end', response, re.DOTALL)
        if match:
            return match.group(0)

        # If no match, return full response (might be just the DRL)
        return response.strip()

    def _validate_drl_syntax(self, drl_content: str) -> Dict[str, Any]:
        """
        Validate DRL syntax
        Basic validation - in production, use Drools KieBuilder
        """
        errors = []

        # Check for required components
        if not re.search(r'rule\s+"[^"]+"', drl_content):
            errors.append("Missing rule declaration with name")

        if "when" not in drl_content:
            errors.append("Missing 'when' clause")

        if "then" not in drl_content:
            errors.append("Missing 'then' clause")

        if not drl_content.strip().endswith("end"):
            errors.append("Missing 'end' keyword")

        # Check for common mistakes
        if re.search(r'\$\w+\s*:', drl_content):
            # Has variable bindings, check for update/modify
            if "update(" not in drl_content and "modify(" not in drl_content:
                errors.append("Warning: Variables modified but no update() call")

        # Check for balanced parentheses
        if drl_content.count("(") != drl_content.count(")"):
            errors.append("Unbalanced parentheses")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": [e for e in errors if e.startswith("Warning:")]
        }

    def _extract_rule_name(self, drl_content: str) -> Optional[str]:
        """Extract rule name from DRL"""
        match = re.search(r'rule\s+"([^"]+)"', drl_content)
        return match.group(1) if match else None

    def _calculate_confidence(
        self,
        drl_content: str,
        validation: Dict[str, Any],
        similar_rules: str
    ) -> float:
        """Calculate confidence score for generated DRL"""
        confidence = 0.5  # Base confidence

        # Boost for valid syntax
        if validation["valid"]:
            confidence += 0.3

        # Boost for proper structure
        if all(keyword in drl_content for keyword in ["when", "then", "end"]):
            confidence += 0.1

        # Boost for variable bindings
        if re.search(r'\$\w+\s*:', drl_content):
            confidence += 0.05

        # Boost for update/modify calls
        if "update(" in drl_content or "modify(" in drl_content:
            confidence += 0.05

        # Penalty for warnings
        if validation.get("warnings"):
            confidence -= 0.1 * len(validation["warnings"])

        return max(0.0, min(1.0, confidence))

    async def refine_drl(
        self,
        drl_content: str,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Refine generated DRL based on user feedback

        Args:
            drl_content: Original DRL
            feedback: User feedback on what to change

        Returns:
            Refined DRL with validation
        """
        system_prompt = """You are refining a Drools DRL rule based on user feedback.
Maintain the original structure but apply the requested changes.
Output only the refined DRL rule."""

        user_prompt = f"""Original DRL:
{drl_content}

User feedback: {feedback}

Generate the refined DRL rule:"""

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            refined_drl = self._extract_drl(response["content"])
            validation = self._validate_drl_syntax(refined_drl)

            return {
                "drl_content": refined_drl,
                "validation": validation,
                "original_drl": drl_content
            }

        except Exception as e:
            logger.error(f"Failed to refine DRL: {str(e)}")
            raise

    async def explain_drl(self, drl_content: str) -> str:
        """
        Generate natural language explanation of DRL rule

        Args:
            drl_content: DRL rule to explain

        Returns:
            Natural language explanation
        """
        system_prompt = """You are explaining a Drools DRL rule in simple terms.
Describe what the rule does, when it triggers, and what actions it takes.
Use plain language that business users can understand."""

        user_prompt = f"""Explain this DRL rule:

{drl_content}

Provide a clear explanation:"""

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            return response["content"]

        except Exception as e:
            logger.error(f"Failed to explain DRL: {str(e)}")
            raise


# Singleton instance
_nl_to_drl_generator: Optional[NLToDRLGenerator] = None


def get_nl_to_drl_generator() -> NLToDRLGenerator:
    """Get or create NLToDRLGenerator singleton"""
    global _nl_to_drl_generator

    if _nl_to_drl_generator is None:
        _nl_to_drl_generator = NLToDRLGenerator()

    return _nl_to_drl_generator
