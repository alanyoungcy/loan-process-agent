"""
Camunda 8 Zeebe Client - Integration with Zeebe Workflow Engine
"""
import httpx
from typing import Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ZeebeClient:
    """Client for communicating with Camunda 8 Zeebe"""

    def __init__(self, gateway_address: str = None):
        self.gateway_address = gateway_address or settings.ZEEBE_GATEWAY_ADDRESS
        self.operate_url = settings.CAMUNDA_OPERATE_URL
        self.tasklist_url = settings.CAMUNDA_TASKLIST_URL

    async def deploy_process(self, process_id: str, bpmn_xml: str) -> Dict[str, Any]:
        """
        Deploy a BPMN process to Zeebe

        Args:
            process_id: Process definition ID
            bpmn_xml: BPMN XML content

        Returns:
            Deployment result
        """
        try:
            # In production, use gRPC client
            # For now, simulate deployment
            logger.info(f"Deploying process {process_id} to Zeebe")

            return {
                "processDefinitionKey": process_id,
                "version": 1,
                "deployed": True
            }

        except Exception as e:
            logger.error(f"Zeebe deployment error: {e}")
            raise Exception(f"Failed to deploy process: {str(e)}")

    async def start_process_instance(
        self,
        process_id: str,
        variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Start a process instance

        Args:
            process_id: Process definition ID
            variables: Process variables

        Returns:
            Process instance details
        """
        try:
            # In production, use gRPC client
            logger.info(f"Starting process instance: {process_id}")

            return {
                "processInstanceKey": f"PI-{process_id}-001",
                "processDefinitionKey": process_id,
                "version": 1,
                "variables": variables or {}
            }

        except Exception as e:
            logger.error(f"Failed to start process instance: {e}")
            raise Exception(f"Failed to start process: {str(e)}")

    async def get_process_instances(self, process_id: str = None) -> List[Dict[str, Any]]:
        """Get active process instances"""
        try:
            # Query Operate API
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.operate_url}/v1/process-instances"
                if process_id:
                    url += f"?processDefinitionKey={process_id}"

                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return []

        except Exception as e:
            logger.error(f"Failed to get process instances: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Zeebe is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check Operate health endpoint
                response = await client.get(f"{self.operate_url}/actuator/health")
                return response.status_code == 200
        except:
            return False


# Singleton instance
zeebe_client = ZeebeClient()
