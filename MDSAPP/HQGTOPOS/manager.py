# MDSAPP/HQGTOPOS/manager.py

import logging
from typing import Dict, Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from pydantic import ValidationError

from MDSAPP.WorkFlowManagement.models.workflow import Workflow, EngineeredWorkflow
from MDSAPP.WorkFlowManagement.models.results import WorkflowExecutionResult
from MDSAPP.core.logging.adk_logging_plugin import MdsLoggingPlugin

# Placeholder imports for agents and managers
# These will be updated to use the actual implementations
from MDSAPP.agents.processor_agent import ProcessorAgent
from MDSAPP.agents.executor_agent import ExecutorAgent
from MDSAPP.agents.engineer_agent import EngineerAgent
from MDSAPP.CasefileManagement.models.casefile import Casefile

logger = logging.getLogger(__name__)

class HQOrchestrator:
    """
    The master orchestrator for the MDS application.
    It manages the overall lifecycle of a mission described in a Casefile.
    """
    def __init__(
        self,
        processor_agent: ProcessorAgent,
        executor_agent: ExecutorAgent,
        engineer_agent: EngineerAgent,
    ):
        self.processor_agent = processor_agent
        self.executor_agent = executor_agent
        self.engineer_agent = engineer_agent
        logger.info("HQOrchestrator initialized.")

    async def run_event_loop(self, casefile: Casefile) -> Casefile:
        """
        Runs the core event loop for a given Casefile.
        This method will orchestrate the agents to process, execute, and engineer a workflow.
        """
        logger.info(f"Starting event loop for casefile: {casefile.id}")

        # 1. Process the mission into a workflow
        if casefile.mission and not casefile.workflows:
            logger.info(f"Delegating to ProcessorAgent for casefile: {casefile.id}")
            casefile = await self._run_processor_agent(casefile)

        # 2. Execute the workflow
        if casefile.workflows and not casefile.execution_results:
            logger.info(f"Delegating to ExecutorAgent for casefile: {casefile.id}")
            casefile = await self._run_executor_agent(casefile)

        # 3. Analyze the results and engineer a new workflow
        if casefile.execution_results and not casefile.engineered_workflows:
            logger.info(f"Delegating to EngineerAgent for casefile: {casefile.id}")
            casefile = await self._run_engineer_agent(casefile)

        logger.info(f"Event loop completed for casefile: {casefile.id}")
        return casefile

    async def _run_processor_agent(self, casefile: Casefile) -> Casefile:
        """Runs the ProcessorAgent to generate a workflow and adds it to the casefile."""
        session_service = InMemorySessionService() # Using in-memory for now
        runner = Runner(
            agent=self.processor_agent,
            app_name="mds7_processor_orchestrator",
            session_service=session_service,
            plugins=[MdsLoggingPlugin()],
        )

        initial_state = {"mission": casefile.mission, "casefile_id": casefile.id}
        session = await session_service.create_session(
            app_name="mds7_processor_orchestrator", 
            user_id="user_orchestrator", 
            state=initial_state
        )

        final_response = None
        async for event in runner.run_async(session_id=session.id):
            if event.is_final_response():
                final_response = event.content.parts[0].text
        
        if final_response:
            try:
                workflow_obj = Workflow.model_validate_json(final_response)
                casefile.workflows.append(workflow_obj)
                casefile.touch()
                logger.info(f"Successfully added new workflow {workflow_obj.workflow_id} to casefile {casefile.id}")
            except ValidationError as e:
                logger.error(f"Failed to validate workflow from ProcessorAgent: {e}")
        else:
            logger.error("ProcessorAgent did not return a final response.")

        return casefile

    async def _run_executor_agent(self, casefile: Casefile) -> Casefile:
        """Runs the ExecutorAgent to execute a workflow and adds the result to the casefile."""
        if not casefile.workflows:
            logger.error("No workflows found in casefile to execute.")
            return casefile

        # For the POC, we execute the first workflow in the list
        workflow_to_execute = casefile.workflows[0]

        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.executor_agent,
            app_name="mds7_executor_orchestrator",
            session_service=session_service,
            plugins=[MdsLoggingPlugin()],
        )

        initial_state = {"workflow": workflow_to_execute.model_dump(), "casefile_id": casefile.id}
        session = await session_service.create_session(
            app_name="mds7_executor_orchestrator",
            user_id="user_orchestrator",
            state=initial_state
        )

        final_response = None
        async for event in runner.run_async(session_id=session.id):
            if event.is_final_response():
                final_response = event.content.parts[0].text

        if final_response:
            try:
                result_obj = WorkflowExecutionResult.model_validate_json(final_response)
                casefile.execution_results.append(result_obj)
                casefile.touch()
                logger.info(f"Successfully added new execution result to casefile {casefile.id}")
            except ValidationError as e:
                logger.error(f"Failed to validate execution result from ExecutorAgent: {e}")
        else:
            logger.error("ExecutorAgent did not return a final response.")

        return casefile

    async def _run_engineer_agent(self, casefile: Casefile) -> Casefile:
        """Runs the EngineerAgent to create an EngineeredWorkflow and adds it to the casefile."""
        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.engineer_agent,
            app_name="mds7_engineer_orchestrator",
            session_service=session_service,
            plugins=[MdsLoggingPlugin()],
        )

        initial_state = {"casefile_id": casefile.id}
        session = await session_service.create_session(
            app_name="mds7_engineer_orchestrator",
            user_id="user_orchestrator",
            state=initial_state
        )

        final_response = None
        async for event in runner.run_async(session_id=session.id):
            if event.is_final_response():
                final_response = event.content.parts[0].text

        if final_response:
            try:
                engineered_workflow_obj = EngineeredWorkflow.model_validate_json(final_response)
                casefile.engineered_workflows.append(engineered_workflow_obj)
                casefile.touch()
                logger.info(f"Successfully added new engineered workflow to casefile {casefile.id}")
            except ValidationError as e:
                logger.error(f"Failed to validate engineered workflow from EngineerAgent: {e}")
        else:
            logger.error("EngineerAgent did not return a final response.")

        return casefile
