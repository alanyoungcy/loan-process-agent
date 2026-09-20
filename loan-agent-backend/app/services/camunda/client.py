"""
Camunda Client - Integration with Camunda BPMN Engine
"""
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CamundaClient:
    """Client for communicating with Camunda BPMN engine"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.CAMUNDA_URL

    async def start_process(
        self,
        process_key: str,
        business_key: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Start a BPMN process instance

        Args:
            process_key: BPMN process definition key
            business_key: Business identifier (e.g., case_id)
            variables: Process variables

        Returns:
            Process instance ID
        """
        try:
            # Convert variables to Camunda format
            camunda_vars = {
                key: {"value": value, "type": "String" if isinstance(value, str) else "Integer"}
                for key, value in variables.items()
            }

            payload = {
                "businessKey": business_key,
                "variables": camunda_vars
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/process-definition/key/{process_key}/start",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("id")

        except httpx.HTTPError as e:
            logger.error(f"Camunda service error: {e}")
            raise Exception(f"Failed to start process: {str(e)}")

    async def get_process_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get process instance details"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/process-instance/{instance_id}"
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get process instance: {e}")
            return {}

    async def get_tasks(
        self,
        process_instance_id: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks for a process instance or assignee"""
        try:
            params = {}
            if process_instance_id:
                params["processInstanceId"] = process_instance_id
            if assignee:
                params["assignee"] = assignee

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/task",
                    params=params
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get tasks: {e}")
            return []

    async def complete_task(
        self,
        task_id: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Complete a user task"""
        try:
            payload = {}
            if variables:
                payload["variables"] = {
                    key: {"value": value}
                    for key, value in variables.items()
                }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/task/{task_id}/complete",
                    json=payload
                )
                response.raise_for_status()
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to complete task: {e}")
            return False

    async def get_process_definitions(self) -> List[Dict[str, Any]]:
        """List all deployed process definitions"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/process-definition"
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get process definitions: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Camunda service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/engine")
                return response.status_code == 200
        except:
            return False


# Singleton instance
camunda_client = CamundaClient()
