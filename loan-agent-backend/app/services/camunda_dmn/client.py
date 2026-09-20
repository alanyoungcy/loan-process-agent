"""
Camunda DMN Client - Integration with Camunda DMN Engine
"""
import httpx
from typing import Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CamundaDmnClient:
    """Client for communicating with Camunda DMN microservice"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.CAMUNDA_DMN_URL

    async def evaluate_case(self, case_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a case against business rules

        Args:
            case_facts: Dictionary containing case data

        Returns:
            Rule execution results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/rules/evaluate",
                    json=case_facts
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Camunda DMN service error: {e}")
            raise Exception(f"Failed to evaluate rules: {str(e)}")

    async def list_rules(self) -> List[Dict[str, Any]]:
        """List all available rules"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/rules/list")
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to list rules: {e}")
            return {"total_rules": 0, "categories": []}

    async def health_check(self) -> bool:
        """Check if Camunda DMN service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/rules/health")
                return response.status_code == 200
        except:
            return False


# Singleton instance
camunda_dmn_client = CamundaDmnClient()

# Backward compatibility alias
drools_client = camunda_dmn_client
DroolsClient = CamundaDmnClient
