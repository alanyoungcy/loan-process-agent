"""
Compliance Checker

Checks text for FDCPA compliance and forbidden phrases
"""
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Check collection communications for compliance"""

    # FDCPA forbidden phrases
    FORBIDDEN_PHRASES = [
        "jail",
        "prison",
        "arrest",
        "sue you",
        "legal action immediately",
        "criminal charges",
        "police",
        "sheriff",
        "warrant",
        "seize your property",
        "garnish your wages",
        "deadbeat",
        "bad person",
        "irresponsible",
        "dishonest",
        "you must pay now",
        "pay today or else",
        "final warning",
        "last chance",
        "contact your employer",
        "tell your family",
        "tell your friends",
        "ruin your credit forever",
        "you will regret",
        "you have no choice",
    ]

    # Warning phrases that require context
    WARNING_PHRASES = [
        "legal action",
        "court",
        "attorney",
        "lawsuit",
        "judgment",
        "credit report",
        "collection agency",
    ]

    # Required disclosures
    REQUIRED_DISCLOSURES = [
        "This is an attempt to collect a debt",
        "Any information obtained will be used for that purpose",
    ]

    def check_compliance(
        self,
        text: str,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Check text for FDCPA compliance

        Args:
            text: Text to check
            include_suggestions: Include improvement suggestions

        Returns:
            {
                "compliant": True/False,
                "forbidden_phrases": ["phrase1", "phrase2"],
                "warning_phrases": ["phrase1"],
                "missing_disclosures": ["disclosure1"],
                "suggestions": ["suggestion1"],
                "severity": "high"|"medium"|"low"
            }
        """
        text_lower = text.lower()

        result = {
            "compliant": True,
            "forbidden_phrases": [],
            "warning_phrases": [],
            "missing_disclosures": [],
            "suggestions": [],
            "severity": "low"
        }

        # Check forbidden phrases
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase.lower() in text_lower:
                result["forbidden_phrases"].append(phrase)
                result["compliant"] = False
                result["severity"] = "high"

        # Check warning phrases
        for phrase in self.WARNING_PHRASES:
            if phrase.lower() in text_lower:
                result["warning_phrases"].append(phrase)
                if result["severity"] == "low":
                    result["severity"] = "medium"

        # Check required disclosures (for letters)
        if len(text) > 200:  # Only check for longer communications
            for disclosure in self.REQUIRED_DISCLOSURES:
                if disclosure.lower() not in text_lower:
                    result["missing_disclosures"].append(disclosure)
                    if result["severity"] == "low":
                        result["severity"] = "medium"

        # Add suggestions if requested
        if include_suggestions:
            result["suggestions"] = self._generate_suggestions(result)

        logger.info(
            f"Compliance check: {result['severity']} - "
            f"Forbidden: {len(result['forbidden_phrases'])}, "
            f"Warnings: {len(result['warning_phrases'])}"
        )

        return result

    def _generate_suggestions(self, check_result: Dict[str, Any]) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []

        if check_result["forbidden_phrases"]:
            suggestions.append(
                "Remove threatening or harassing language. Focus on factual "
                "information about the debt."
            )

        if "jail" in check_result["forbidden_phrases"] or \
           "prison" in check_result["forbidden_phrases"]:
            suggestions.append(
                "Never threaten imprisonment for debt. This is illegal and "
                "a serious FDCPA violation."
            )

        if "arrest" in check_result["forbidden_phrases"]:
            suggestions.append(
                "Do not threaten arrest. Civil debt cannot result in arrest."
            )

        if check_result["warning_phrases"]:
            if "legal action" in check_result["warning_phrases"]:
                suggestions.append(
                    "When mentioning legal action, ensure it is a legitimate "
                    "possibility and clearly state it is not a threat."
                )

            if "credit report" in check_result["warning_phrases"]:
                suggestions.append(
                    "Credit reporting statements must be accurate. State facts, "
                    "not threats."
                )

        if check_result["missing_disclosures"]:
            suggestions.append(
                "Include required FDCPA disclosures: 'This is an attempt to "
                "collect a debt. Any information obtained will be used for "
                "that purpose.'"
            )

        if not suggestions:
            suggestions.append(
                "Communication appears compliant. Continue using professional, "
                "factual language."
            )

        return suggestions

    def suggest_alternatives(self, forbidden_phrase: str) -> str:
        """Suggest alternative wording for forbidden phrases"""
        alternatives = {
            "jail": "legal consequences may include judgment",
            "arrest": "legal action may be taken",
            "sue you": "legal remedies may be pursued",
            "deadbeat": "customer with outstanding balance",
            "you must pay now": "payment is requested",
            "pay today or else": "please contact us to discuss payment options",
            "final warning": "this is an important notice",
            "contact your employer": "we may need to verify employment",
        }

        return alternatives.get(
            forbidden_phrase.lower(),
            "use professional, factual language"
        )

    def validate_contact_time(self, hour: int, day_of_week: int) -> Dict[str, Any]:
        """
        Validate if contact time is FDCPA compliant

        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)

        Returns:
            {
                "allowed": True/False,
                "reason": "explanation"
            }
        """
        # FDCPA allows contact 8 AM - 9 PM local time
        if hour < 8:
            return {
                "allowed": False,
                "reason": "Contact before 8 AM is prohibited by FDCPA"
            }

        if hour >= 21:
            return {
                "allowed": False,
                "reason": "Contact after 9 PM is prohibited by FDCPA"
            }

        # Weekend contact is generally allowed but discouraged
        if day_of_week >= 5:  # Saturday or Sunday
            return {
                "allowed": True,
                "reason": "Weekend contact allowed but use discretion"
            }

        return {
            "allowed": True,
            "reason": "Contact time is compliant"
        }


# Global instance
compliance_checker = ComplianceChecker()
