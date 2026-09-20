"""
Workflow API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.workflows.engine import workflow_engine, WorkflowStatus
from app.workflows.definitions.collection_workflows import register_all_workflows

router = APIRouter(tags=["Workflows"])


class StartWorkflowRequest(BaseModel):
    """Request to start a workflow"""
    workflow_key: str
    business_key: str
    variables: Dict[str, Any] = {}


class CompleteTaskRequest(BaseModel):
    """Request to complete a task"""
    variables: Dict[str, Any] = {}


class WorkflowInstanceResponse(BaseModel):
    """Workflow instance information"""
    id: str
    workflow_key: str
    status: str
    business_key: str
    current_task: Optional[str]
    created_at: str
    completed_at: Optional[str]


class TaskResponse(BaseModel):
    """Task information"""
    instance_id: str
    task_id: str
    task_name: str
    business_key: str
    due_date: Optional[str]


# Initialize workflows on module load
register_all_workflows()


@router.post("/start", response_model=WorkflowInstanceResponse)
async def start_workflow(
    request: StartWorkflowRequest
):
    """
    Start a new workflow instance

    Initiates a workflow for a specific case

    - **workflow_key**: Key of workflow to start
    - **business_key**: Case ID or business identifier
    - **variables**: Initial workflow variables
    """
    try:
        instance = workflow_engine.start_workflow(
            workflow_key=request.workflow_key,
            business_key=request.business_key,
            variables=request.variables
        )

        return WorkflowInstanceResponse(
            id=instance.id,
            workflow_key=instance.workflow_key,
            status=instance.status.value,
            business_key=instance.business_key,
            current_task=instance.current_task,
            created_at=instance.created_at.isoformat(),
            completed_at=instance.completed_at.isoformat() if instance.completed_at else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/definitions")
async def list_workflow_definitions():
    """
    List all available workflow definitions

    Returns all registered workflow templates
    """
    definitions = []

    for key, definition in workflow_engine.definitions.items():
        definitions.append({
            "key": definition.key,
            "name": definition.name,
            "description": definition.description,
            "version": definition.version,
            "enabled": definition.enabled,
            "num_tasks": len(definition.tasks)
        })

    return {"workflows": definitions}


@router.get("/instances/{instance_id}")
async def get_workflow_instance(
    instance_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workflow instance details

    Returns complete information about a workflow instance
    """
    instance = workflow_engine.get_instance(instance_id)

    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return {
        "id": instance.id,
        "workflow_key": instance.workflow_key,
        "status": instance.status.value,
        "business_key": instance.business_key,
        "variables": instance.variables,
        "current_task": instance.current_task,
        "tasks": [
            {
                "id": task.id,
                "name": task.name,
                "type": task.task_type,
                "status": task.status.value,
                "assignee": task.assignee,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in instance.tasks
        ],
        "created_at": instance.created_at.isoformat(),
        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
        "error": instance.error
    }


@router.get("/instances/business-key/{business_key}")
async def get_instances_by_business_key(
    business_key: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all workflow instances for a business key (case ID)

    Returns all workflows associated with a specific case
    """
    instances = workflow_engine.get_instances_by_business_key(business_key)

    return {
        "business_key": business_key,
        "instances": [
            {
                "id": inst.id,
                "workflow_key": inst.workflow_key,
                "status": inst.status.value,
                "current_task": inst.current_task,
                "created_at": inst.created_at.isoformat()
            }
            for inst in instances
        ]
    }


@router.get("/tasks/my-tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get tasks assigned to current user

    Returns all active workflow tasks assigned to the logged-in user
    """
    tasks = workflow_engine.get_user_tasks(current_user.get("username"))

    return [
        TaskResponse(
            instance_id=task["instance_id"],
            task_id=task["task_id"],
            task_name=task["task_name"],
            business_key=task["business_key"],
            due_date=task["due_date"].isoformat() if task["due_date"] else None
        )
        for task in tasks
    ]


@router.post("/tasks/{instance_id}/{task_id}/complete")
async def complete_task(
    instance_id: str,
    task_id: str,
    request: CompleteTaskRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Complete a workflow task

    Marks a task as complete and advances the workflow

    - **instance_id**: Workflow instance ID
    - **task_id**: Task ID to complete
    - **variables**: Output variables from task
    """
    try:
        workflow_engine.complete_task(
            instance_id=instance_id,
            task_id=task_id,
            variables=request.variables
        )

        return {"message": "Task completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/instances/{instance_id}/cancel")
async def cancel_workflow(
    instance_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Cancel a running workflow instance

    Stops workflow execution and cancels all active tasks
    """
    # Allow all authenticated users to cancel workflows
    try:
        workflow_engine.cancel_instance(instance_id)
        return {"message": "Workflow cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics")
async def get_workflow_statistics(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workflow engine statistics

    Returns statistics about workflow execution
    """
    stats = workflow_engine.get_statistics()
    return stats



@router.get("/instances/active/{workflow_key}")
async def get_active_instances(workflow_key: str):
    """
    Get active instances for a specific workflow
    
    Args:
        workflow_key: The workflow key to filter by
        
    Returns:
        List of active workflow instances
    """
    instances = [
        inst for inst in workflow_engine.instances.values()
        if inst.workflow_key == workflow_key and inst.status == WorkflowStatus.RUNNING
    ]
    
    return [{
        "id": inst.id,
        "workflow_key": inst.workflow_key,
        "status": inst.status.value,
        "business_key": inst.business_key,
        "current_task": inst.current_task,
        "created_at": inst.created_at.isoformat(),
    } for inst in instances]

@router.get("/instances")
async def list_workflow_instances(
    status: Optional[str] = None,
    workflow_key: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    List all workflow instances

    Optional filters:
    - **status**: Filter by workflow status
    - **workflow_key**: Filter by workflow type
    """
    instances = list(workflow_engine.instances.values())

    # Apply filters
    if status:
        instances = [i for i in instances if i.status.value == status]

    if workflow_key:
        instances = [i for i in instances if i.workflow_key == workflow_key]

    return {
        "total": len(instances),
        "instances": [
            {
                "id": inst.id,
                "workflow_key": inst.workflow_key,
                "status": inst.status.value,
                "business_key": inst.business_key,
                "current_task": inst.current_task,
                "created_at": inst.created_at.isoformat()
            }
            for inst in instances
        ]
    }


@router.get("/definitions/{workflow_key}/diagram")
async def get_workflow_diagram(
    workflow_key: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get BPMN diagram representation of workflow

    Returns workflow structure in a format suitable for visualization
    with React Flow or BPMN.js
    """
    definition = workflow_engine.definitions.get(workflow_key)

    if not definition:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Convert workflow definition to diagram format
    nodes = []
    edges = []

    # Add start node
    nodes.append({
        "id": "start",
        "type": "startEvent",
        "data": {"label": "Start"},
        "position": {"x": 50, "y": 150}
    })

    # Add task nodes
    x_offset = 200
    for idx, task in enumerate(definition.tasks):
        task_id = f"task_{idx}"
        nodes.append({
            "id": task_id,
            "type": "userTask" if task.get("type") == "user_task" else "serviceTask",
            "data": {
                "label": task.get("name", f"Task {idx+1}"),
                "description": task.get("description", ""),
                "assignee": task.get("assignee"),
                "duration": task.get("estimated_duration")
            },
            "position": {"x": x_offset + (idx * 200), "y": 150}
        })

        # Add edge from previous node
        if idx == 0:
            edges.append({
                "id": f"e_start_{task_id}",
                "source": "start",
                "target": task_id,
                "animated": True
            })
        else:
            edges.append({
                "id": f"e_task_{idx-1}_{idx}",
                "source": f"task_{idx-1}",
                "target": task_id,
                "animated": True
            })

    # Add end node
    end_x = x_offset + (len(definition.tasks) * 200)
    nodes.append({
        "id": "end",
        "type": "endEvent",
        "data": {"label": "End"},
        "position": {"x": end_x, "y": 150}
    })

    # Connect last task to end
    if definition.tasks:
        edges.append({
            "id": f"e_task_{len(definition.tasks)-1}_end",
            "source": f"task_{len(definition.tasks)-1}",
            "target": "end",
            "animated": True
        })

    return {
        "workflow_key": workflow_key,
        "name": definition.name,
        "version": definition.version,
        "nodes": nodes,
        "edges": edges
    }


@router.get("/definitions/{workflow_key}/stats")
async def get_workflow_stats(
    workflow_key: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get statistics for a specific workflow

    Returns execution metrics and performance data
    """
    definition = workflow_engine.definitions.get(workflow_key)

    if not definition:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Get instances for this workflow
    instances = [i for i in workflow_engine.instances.values()
                 if i.workflow_key == workflow_key]

    active_instances = [i for i in instances if i.status == WorkflowStatus.RUNNING]
    completed_instances = [i for i in instances if i.status == WorkflowStatus.COMPLETED]
    failed_instances = [i for i in instances if i.status == WorkflowStatus.FAILED]

    # Calculate average duration for completed instances
    if completed_instances:
        durations = [
            (i.completed_at - i.created_at).total_seconds() / 86400  # days
            for i in completed_instances if i.completed_at
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
    else:
        avg_duration = 0

    # Count completed today
    today = datetime.now().date()
    completed_today = len([
        i for i in completed_instances
        if i.completed_at and i.completed_at.date() == today
    ])

    return {
        "workflow_key": workflow_key,
        "name": definition.name,
        "total_instances": len(instances),
        "active_instances": len(active_instances),
        "completed_instances": len(completed_instances),
        "failed_instances": len(failed_instances),
        "completed_today": completed_today,
        "avg_duration_days": round(avg_duration, 1),
        "success_rate": round(len(completed_instances) / len(instances) * 100, 1) if instances else 0
    }
