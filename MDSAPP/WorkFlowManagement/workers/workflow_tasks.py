# MDSAPP/WorkFlowManagement/workers/workflow_tasks.py

import logging
import asyncio
import os

from MDSAPP.celery import app
from MDSAPP.core.dependencies import get_hq_orchestrator, get_session_service
from MDSAPP.core.managers.pubsub_manager import PubSubManager
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

TASK_STATUS_TOPIC = os.getenv("MDS_TASK_STATUS_TOPIC", "mds-task-status")

@app.task(bind=True, name="mds.run_orchestration")
def run_orchestration_task(self, casefile_id: str):
    """
    The main Celery task that orchestrates the entire workflow for a given casefile.
    """
    pubsub_manager = PubSubManager()
    task_id = self.request.id

    # Publish start message
    asyncio.run(pubsub_manager.publish_message(
        TASK_STATUS_TOPIC,
        {"task_id": task_id, "casefile_id": casefile_id, "status": "STARTED"}
    ))

    logger.info(f"[Celery Task] Starting orchestration for casefile_id: {casefile_id}")
    logger.info(f"GOOGLE_APPLICATION_CREDENTIALS in worker: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    try:
        hq_orchestrator = get_hq_orchestrator()
        session_service = get_session_service()

        # Create a session for the orchestrator
        session = asyncio.run(session_service.create_session(
            app_name="MDSAPP",
            user_id="celery_worker", # User ID for the worker
            session_id=casefile_id,
            state={"casefile_id": casefile_id}
        ))

        # Create an InvocationContext for the orchestrator
        ctx = InvocationContext(
            session=session,
            session_service=session_service,
            invocation_id=self.request.id, # Use Celery task ID as invocation ID
            agent=hq_orchestrator
        )

        # Run the orchestrator's async generator within asyncio.run
        final_response_content = None
        async def _run_orchestrator_async():
            nonlocal final_response_content
            async for event in hq_orchestrator._run_async_impl(ctx):
                if event.is_final_response():
                    final_response_content = event.content.parts[0].text
                    logger.info(f"Orchestrator final response for {casefile_id}: {final_response_content}")
                elif event.content and event.content.parts:
                    logger.info(f"Orchestrator intermediate event for {casefile_id} from {event.author}: {event.content.parts[0].text}")

        asyncio.run(_run_orchestrator_async())

        if final_response_content:
            self.update_state(state='SUCCESS', meta={'status': 'Orchestration complete', 'result': final_response_content})
            asyncio.run(pubsub_manager.publish_message(
                TASK_STATUS_TOPIC,
                {"task_id": task_id, "casefile_id": casefile_id, "status": "SUCCESS", "result": final_response_content}
            ))
            return {'status': 'SUCCESS', 'casefile_id': casefile_id, 'result': final_response_content}
        else:
            self.update_state(state='FAILURE', meta={'status': 'Orchestration completed without a final response'})
            asyncio.run(pubsub_manager.publish_message(
                TASK_STATUS_TOPIC,
                {"task_id": task_id, "casefile_id": casefile_id, "status": "FAILURE", "result": "No final response"}
            ))
            return {'status': 'FAILURE', 'casefile_id': casefile_id, 'result': 'No final response'}

    except Exception as e:
        logger.error(f"Error in orchestration task for {casefile_id}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        asyncio.run(pubsub_manager.publish_message(
            TASK_STATUS_TOPIC,
            {"task_id": task_id, "casefile_id": casefile_id, "status": "FAILURE", "error": str(e)}
        ))
        raise