"""
Camunda Operate API integration
Fetch process definitions and instances from Camunda Operate
"""
from typing import List, Dict, Any
import httpx
from app.core.config import settings


class CamundaOperateClient:
    """Client for Camunda Operate REST API"""

    def __init__(self):
        self.base_url = "http://localhost:8080/v1"
        self.timeout = 10.0

    async def get_process_definitions(self) -> List[Dict[str, Any]]:
        """Fetch all deployed process definitions from Camunda Operate"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/process-definitions/search",
                    json={"filter": {}, "size": 100},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                elif response.status_code == 403:
                    # Operate has auth enabled, return empty for now
                    print("Camunda Operate requires authentication")
                    return []
                else:
                    print(f"Error fetching from Operate: {response.status_code}")
                    return []
        except Exception as e:
            print(f"Error connecting to Camunda Operate: {e}")
            return []

    async def get_decision_definitions(self) -> List[Dict[str, Any]]:
        """Fetch all deployed DMN decision definitions"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/decision-definitions/search",
                    json={"filter": {}, "size": 100},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                else:
                    return []
        except Exception as e:
            print(f"Error fetching decisions from Operate: {e}")
            return []


# Global client instance
camunda_operate = CamundaOperateClient()
