# MDSAPP/agents/api.py

import logging
from fastapi import APIRouter, Depends, HTTPException

# Import dependencies from the new MDSAPP core
from MDSAPP.core.dependencies import get_workflow_manager, get_casefile_manager
from MDSAPP.WorkFlowManagement.manager import WorkflowManager
from MDSAPP.CasefileManagement.manager import CasefileManager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/orchestrator/run/{casefile_id}", status_code=202)
async def trigger_orchestrator(
    casefile_id: str,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    casefile_manager: CasefileManager = Depends(get_casefile_manager)
):
    """
    Triggers the full HQ orchestration flow for a given casefile ID.
    This is now an asynchronous task managed by Celery.
    """
    logger.info(f"API call received: Triggering HQOrchestrator for casefile_id: {casefile_id}")
    
    # Check if the casefile exists
    casefile = await casefile_manager.load_casefile(casefile_id)
    if not casefile:
        raise HTTPException(status_code=404, detail=f"Casefile with ID '{casefile_id}' not found.")

    task_info = workflow_manager.start_orchestration(casefile_id)
    return {"message": "Orchestrator task initiated.", "casefile_id": casefile_id, "task_id": task_info["task_id"]}
