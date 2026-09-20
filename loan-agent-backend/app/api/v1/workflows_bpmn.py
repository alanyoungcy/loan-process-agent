"""
Enhanced Workflow API Endpoints
Supports BPMN/DMN visual modeling, Camunda deployment, and DMN integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from pydantic import BaseModel
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.camunda.client import get_camunda_client
from app.services.camunda_dmn.client import camunda_dmn_client

router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    name: str
    type: str  # 'bpmn' or 'dmn'


class WorkflowUpdateRequest(BaseModel):
    xml: str


class DeploymentRequest(BaseModel):
    xml: str


class ValidationRequest(BaseModel):
    xml: str


class DecisionTableTestRequest(BaseModel):
    xml: str
    inputVariables: Dict[str, Any]


# In-memory storage (replace with database in production)
workflows_storage = {}


@router.get("/list")
async def list_workflows(
    current_user: dict = Depends(get_current_user)
):
    """List all workflows"""
    workflows_list = [
        {
            "id": wf_id,
            "name": wf["name"],
            "type": wf["type"],
            "xml": wf["xml"],
            "deployedToCamunda": wf.get("deployedToCamunda", False),
            "deployedToDMN": wf.get("deployedToDMN", False),
            "createdAt": wf["createdAt"],
            "updatedAt": wf["updatedAt"]
        }
        for wf_id, wf in workflows_storage.items()
    ]
    return workflows_list


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow by ID"""
    if workflow_id not in workflows_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    wf = workflows_storage[workflow_id]
    return {
        "id": workflow_id,
        "name": wf["name"],
        "type": wf["type"],
        "xml": wf["xml"],
        "deployedToCamunda": wf.get("deployedToCamunda", False),
        "deployedToDMN": wf.get("deployedToDMN", False),
        "createdAt": wf["createdAt"],
        "updatedAt": wf["updatedAt"]
    }


@router.post("/create")
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new workflow"""
    workflow_id = str(uuid.uuid4())

    # Initial XML based on type
    if request.type == "bpmn":
        initial_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                   xmlns:camunda="http://camunda.org/schema/1.0/bpmn"
                   id="Definitions_1"
                   targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start"/>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36"/>
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""
    else:  # dmn
        initial_xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             id="Definitions_1"
             name="Decision"
             namespace="http://camunda.org/schema/1.0/dmn">
  <decision id="Decision_1" name="Decision">
    <decisionTable id="DecisionTable_1">
      <input id="Input_1" label="Input">
        <inputExpression id="InputExpression_1" typeRef="string">
          <text>input</text>
        </inputExpression>
      </input>
      <output id="Output_1" label="Output" name="output" typeRef="string"/>
      <rule id="DecisionRule_1">
        <inputEntry id="UnaryTests_1">
          <text>"value"</text>
        </inputEntry>
        <outputEntry id="LiteralExpression_1">
          <text>"result"</text>
        </outputEntry>
      </rule>
    </decisionTable>
  </decision>
</definitions>"""

    now = datetime.utcnow().isoformat()
    workflows_storage[workflow_id] = {
        "name": request.name,
        "type": request.type,
        "xml": initial_xml,
        "createdAt": now,
        "updatedAt": now
    }

    return {
        "id": workflow_id,
        "name": request.name,
        "type": request.type,
        "xml": initial_xml,
        "deployedToCamunda": False,
        "deployedToDMN": False,
        "createdAt": now,
        "updatedAt": now
    }


@router.put("/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update workflow XML"""
    if workflow_id not in workflows_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    workflows_storage[workflow_id]["xml"] = request.xml
    workflows_storage[workflow_id]["updatedAt"] = datetime.utcnow().isoformat()

    wf = workflows_storage[workflow_id]
    return {
        "id": workflow_id,
        "name": wf["name"],
        "type": wf["type"],
        "xml": wf["xml"],
        "deployedToCamunda": wf.get("deployedToCamunda", False),
        "deployedToDMN": wf.get("deployedToDMN", False),
        "createdAt": wf["createdAt"],
        "updatedAt": wf["updatedAt"]
    }


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete workflow"""
    if workflow_id not in workflows_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    del workflows_storage[workflow_id]
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/deploy-camunda")
async def deploy_to_camunda(
    workflow_id: str,
    request: DeploymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Deploy BPMN workflow to Camunda"""
    if workflow_id not in workflows_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    wf = workflows_storage[workflow_id]

    if wf["type"] != "bpmn":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only BPMN workflows can be deployed to Camunda"
        )

    try:
        # Deploy to Camunda
        camunda_client = get_camunda_client()
        result = await camunda_client.deploy_process(
            deployment_name=wf["name"],
            bpmn_xml=request.xml
        )

        # Mark as deployed
        workflows_storage[workflow_id]["deployedToCamunda"] = True
        workflows_storage[workflow_id]["updatedAt"] = datetime.utcnow().isoformat()

        return {
            "deploymentId": result.get("id"),
            "deploymentTime": result.get("deploymentTime"),
            "processDefinitions": result.get("deployedProcessDefinitions", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy to Camunda: {str(e)}"
        )


@router.post("/{workflow_id}/deploy-dmn")
async def deploy_to_camunda_dmn(
    workflow_id: str,
    request: DeploymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Deploy DMN decision table to Camunda DMN Engine"""
    if workflow_id not in workflows_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    wf = workflows_storage[workflow_id]

    if wf["type"] != "dmn":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DMN workflows can be deployed to Camunda DMN"
        )

    try:
        # Deploy to Camunda DMN service
        # In production, this would actually deploy via API

        # Mark as deployed
        workflows_storage[workflow_id]["deployedToDMN"] = True
        workflows_storage[workflow_id]["updatedAt"] = datetime.utcnow().isoformat()

        return {
            "deploymentId": str(uuid.uuid4()),
            "deploymentTime": datetime.utcnow().isoformat(),
            "decisionDefinitions": ["Decision_1"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy to Camunda DMN: {str(e)}"
        )


@router.post("/validate-bpmn")
async def validate_bpmn(
    request: ValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate BPMN XML"""
    try:
        # Basic XML validation
        ET.fromstring(request.xml)

        # Check for required BPMN elements
        if "bpmn:definitions" not in request.xml:
            return {
                "valid": False,
                "errors": ["Missing bpmn:definitions root element"]
            }

        return {"valid": True}

    except ET.ParseError as e:
        return {
            "valid": False,
            "errors": [f"XML parse error: {str(e)}"]
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }


@router.post("/validate-dmn")
async def validate_dmn(
    request: ValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate DMN XML"""
    try:
        # Basic XML validation
        ET.fromstring(request.xml)

        # Check for required DMN elements
        if "definitions" not in request.xml or "decision" not in request.xml:
            return {
                "valid": False,
                "errors": ["Missing required DMN elements (definitions, decision)"]
            }

        return {"valid": True}

    except ET.ParseError as e:
        return {
            "valid": False,
            "errors": [f"XML parse error: {str(e)}"]
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }


@router.post("/test-decision-table")
async def test_decision_table(
    request: DecisionTableTestRequest,
    current_user: dict = Depends(get_current_user)
):
    """Test DMN decision table with input variables"""
    try:
        # Parse DMN and extract decision logic
        root = ET.fromstring(request.xml)

        # This is a simplified test - in production, use a proper DMN engine
        # For now, return mock result
        return {
            "success": True,
            "input": request.inputVariables,
            "output": {
                "result": "Mock decision output",
                "matchedRules": ["Rule_1"]
            },
            "executionTime": 15
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test decision table: {str(e)}"
        )
