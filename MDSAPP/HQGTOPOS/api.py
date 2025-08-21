
from fastapi import APIRouter, HTTPException, Depends
import logging

from MDSAPP.core.dependencies import get_casefile_manager, get_workflow_manager
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.WorkFlowManagement.manager import WorkflowManager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/hq/run/{casefile_id}", tags=["HQ Orchestrator"], status_code=202)
async def run_hq_orchestrator(
    casefile_id: str,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    workflow_manager: WorkflowManager = Depends(get_workflow_manager)
):
    """
    Triggers the full HQ orchestration flow for a given casefile ID.
    This is now an asynchronous task managed by Celery.
    """
    logger.info(f"Received request to run HQ flow for casefile: {casefile_id}")
    
    # Check if the casefile exists
    casefile = await casefile_manager.load_casefile(casefile_id)
    if not casefile:
        raise HTTPException(status_code=404, detail=f"Casefile with ID '{casefile_id}' not found.")

    task_info = workflow_manager.start_orchestration(casefile_id)
    return {"message": f"HQ orchestration for casefile {casefile_id} initiated successfully.", "task_id": task_info["task_id"]}
