"""
Deployment endpoints for Camunda workflows and decisions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.camunda_deployment import camunda_deployment
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class DeployBpmnRequest(BaseModel):
    name: str
    bpmn_xml: str


class DeployDmnRequest(BaseModel):
    name: str
    dmn_xml: str


@router.post("/deploy/bpmn")
async def deploy_bpmn(request: DeployBpmnRequest):
    """
    Deploy BPMN workflow to Camunda 8
    """
    try:
        result = await camunda_deployment.deploy_bpmn(
            name=request.name,
            bpmn_xml=request.bpmn_xml
        )

        if result["success"]:
            return {
                "message": result["message"],
                "deployed": True
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))

    except Exception as e:
        logger.error(f"Error deploying BPMN: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy/dmn")
async def deploy_dmn(request: DeployDmnRequest):
    """
    Deploy DMN decision to Camunda 8
    """
    try:
        result = await camunda_deployment.deploy_dmn(
            name=request.name,
            dmn_xml=request.dmn_xml
        )

        if result["success"]:
            return {
                "message": result["message"],
                "deployed": True
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))

    except Exception as e:
        logger.error(f"Error deploying DMN: {e}")
        raise HTTPException(status_code=500, detail=str(e))
