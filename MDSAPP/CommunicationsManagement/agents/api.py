# MDSAPP/agents/api.py

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

# Import dependencies from the new MDSAPP core
from MDSAPP.core.dependencies import get_hq_orchestrator
from MDSAPP.agents.hq_orchestrator import HQOrchestratorAgent

logger = logging.getLogger(__name__)
router = APIRouter()

async def run_orchestration_task(orchestrator: HQOrchestratorAgent, casefile_id: str):
    """The background task that runs the orchestrator."""
    logger.info(f"Background task started: Running HQOrchestrator for casefile_id: {casefile_id}")
    # The ADK runner is not easily accessible here for a full async stream.
    # For now, we simulate the invocation by directly calling the agent's method.
    # This is a simplification for this stage of development.
    # A more robust solution would involve a shared task queue (e.g., Celery) 
    # or a more complex ADK runner setup.
    
    # Mock a simple InvocationContext state
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.sessions import Session, InMemorySessionService
    import uuid

    # In a real app, you would get the session service via DI
    session_service = InMemorySessionService()

    mock_session = Session(
        id=f"mock_session_for_{casefile_id}",
        app_name="MDSAPP_Orchestrator",
        user_id="system_user",
        state={"casefile_id": casefile_id}
    )
    mock_ctx = InvocationContext(
        session=mock_session,
        session_service=session_service,
        invocation_id=str(uuid.uuid4()),
        agent=orchestrator
    )

    try:
        async for event in orchestrator._run_async_impl(mock_ctx):
            logger.info(f"Orchestrator event: {event.content}")
    except Exception as e:
        logger.error(f"Error running orchestration task for {casefile_id}: {e}", exc_info=True)

@router.post("/orchestrator/run/{casefile_id}", status_code=202)
async def trigger_orchestrator(
    casefile_id: str,
    background_tasks: BackgroundTasks,
    orchestrator: HQOrchestratorAgent = Depends(get_hq_orchestrator)
):
    """
    Triggers the HQOrchestrator to run its logic for a given casefile.
    This is the main entry point for starting a mission.
    """
    logger.info(f"API call received: Triggering HQOrchestrator for casefile_id: {casefile_id}")
    background_tasks.add_task(run_orchestration_task, orchestrator, casefile_id)
    return {"message": "Orchestrator task initiated.", "casefile_id": casefile_id}
