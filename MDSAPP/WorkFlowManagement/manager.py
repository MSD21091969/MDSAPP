# MDSAPP/WorkFlowManagement/manager.py

import logging
from typing import Dict
from MDSAPP.celery import app

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Orchestrates workflows by sending asynchronous tasks to Celery.
    """
    def __init__(self):
        logger.info("WorkflowManager (MDSAPP) initialized.")

    def start_orchestration(self, casefile_id: str) -> Dict:
        """
        Starts the main asynchronous orchestration task for a given casefile.
        """
        logger.info(f"Dispatching orchestration task for casefile_id: {casefile_id}")
        task = app.send_task("mds.run_orchestration", kwargs={"casefile_id": casefile_id})
        return {"task_id": task.id, "status": "ORCHESTRATION_STARTED"}
