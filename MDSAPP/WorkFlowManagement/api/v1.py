from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.dependencies import get_current_user_id
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.WorkFlowManagement.utils.casefile_generator import create_real_estate_casefile_with_data
from MDSAPP.CasefileManagement.models.casefile import Casefile
from MDSAPP.celery import app as celery_app

router = APIRouter()

# Dependency to get CasefileManager instance
def get_casefile_manager():
    db_manager = DatabaseManager()
    return CasefileManager(db_manager)

@router.post("/workflow-engineer/create-real-estate-casefile", response_model=Casefile, status_code=status.HTTP_201_CREATED)
async def create_real_estate_casefile(
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    user_id: str = Depends(get_current_user_id)
):
    """
    Endpoint for the Workflow Engineer to create a new real estate market analysis casefile
    with generated sub-casefiles and initial data (description, mission, type).
    """
    try:
        new_casefile = await create_real_estate_casefile_with_data(casefile_manager, user_id)
        return new_casefile
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_task_status(task_id: str):
    """
    Retrieves the status and result of a Celery task.
    """
    task_result = celery_app.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
    return result
