# MDSAPP/core/tools/analysis_tools.py

import logging
from typing import Dict, Any
import datetime

from MDSAPP.WorkFlowManagement.models.results import WorkflowExecutionResult, StepStatus

logger = logging.getLogger(__name__)

def calculate_execution_summary(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates summary statistics from a WorkflowExecutionResult object.

    Args:
        execution_result: A dictionary representing a WorkflowExecutionResult.

    Returns:
        A dictionary with summary statistics.
    """
    logger.info(f"[TOOL] Calculating summary for workflow result: {execution_result.get('result_id')}")

    try:
        # Validate with the Pydantic model
        result_obj = WorkflowExecutionResult(**execution_result)

        total_steps = len(result_obj.steps)
        successful_steps = sum(1 for step in result_obj.steps if step.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for step in result_obj.steps if step.status == StepStatus.FAILED)

        duration = result_obj.ended_at - result_obj.started_at
        duration_seconds = round(duration.total_seconds(), 2)

        summary = {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "duration_seconds": duration_seconds,
        }

        return summary

    except Exception as e:
        logger.error(f"Error calculating execution summary: {e}", exc_info=True)
        return {"error": f"Failed to calculate summary: {str(e)}"}
