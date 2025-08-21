# MDSAPP/agents/hq_orchestrator.py

import logging
import json
import uuid # Added import
from typing import AsyncGenerator

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import AgentTool
from google.genai import types as genai_types

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import Workflow, EngineeredWorkflow
from MDSAPP.WorkFlowManagement.models.results import WorkflowExecutionResult

logger = logging.getLogger(__name__)

class HQOrchestratorAgent(BaseAgent):
    """
    The master orchestrator for the MDS. It is a custom agent that decides
    the next logical step in a mission based on the state of a Casefile.
    """
    _casefile_manager: CasefileManager = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()
    _processor_agent: LlmAgent = PrivateAttr()
    _executor_agent: LlmAgent = PrivateAttr()
    _engineer_agent: LlmAgent = PrivateAttr()

    def __init__(
        self,
        name: str,
        casefile_manager: CasefileManager,
        tool_registry: ToolRegistry,
        processor_agent: LlmAgent,
        executor_agent: LlmAgent,
        engineer_agent: LlmAgent,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._casefile_manager = casefile_manager
        self._tool_registry = tool_registry
        self._processor_agent = processor_agent
        self._executor_agent = executor_agent
        self._engineer_agent = engineer_agent
        logger.info(f"HQOrchestratorAgent initialized.")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        The main script of the application. It inspects the casefile and
        triggers the next logical agent.
        """
        casefile_id = ctx.session.state.get("casefile_id")
        if not casefile_id:
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Error: No casefile_id found in session state.")]))
            return

        casefile = await self._casefile_manager.load_casefile(casefile_id)
        if not casefile:
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error: Casefile {casefile_id} not found.")]))
            return

        # --- Orchestration Logic --- #

        # 1. "Mission to Plan" Workflow
        if casefile.description and not casefile.workflows:
            logger.info(f"Orchestrator: Casefile '{casefile_id}' requires a plan. Delegating to ProcessorAgent.")

            # Create a new InvocationContext for the ProcessorAgent
            processor_session = await ctx.session_service.create_session(
                app_name=ctx.session.app_name,
                user_id=ctx.session.user_id,
                state={"mission": casefile.description, "casefile_id": casefile_id}
            )
            processor_ctx = InvocationContext(
                session=processor_session,
                session_service=ctx.session_service,
                invocation_id=str(uuid.uuid4()),
                agent=self._processor_agent
            )
            async for event in self._processor_agent._run_async_impl(processor_ctx):
                if event.is_final_response():
                    try:
                        workflow_dict = json.loads(event.content.parts[0].text)
                        casefile.workflows.append(Workflow(**workflow_dict))
                        self._casefile_manager.db_manager.save_casefile(casefile)
                        logger.info(f"Orchestrator: Successfully saved new workflow to casefile '{casefile_id}'.")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Plan created for casefile {casefile_id}. Ready for execution.")]))
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Orchestrator: Failed to decode or save workflow. Error: {e}")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error processing plan from ProcessorAgent: {e}")]))
                else:
                    yield event
            return

        # 2. "Plan to Execution" Workflow
        elif casefile.workflows and not casefile.execution_results:
            logger.info(f"Orchestrator: Casefile '{casefile_id}' has a plan. Delegating to ExecutorAgent.")
            workflow_to_execute = casefile.workflows[0]

            # Create a new InvocationContext for the ExecutorAgent
            executor_session = await ctx.session_service.create_session(
                app_name=ctx.session.app_name,
                user_id=ctx.session.user_id,
                state={"workflow": workflow_to_execute.model_dump(), "casefile_id": casefile_id}
            )
            executor_ctx = InvocationContext(
                session=executor_session,
                session_service=ctx.session_service,
                invocation_id=str(uuid.uuid4()),
                agent=self._executor_agent
            )
            async for event in self._executor_agent._run_async_impl(executor_ctx):
                if event.is_final_response():
                    try:
                        result_dict = json.loads(event.content.parts[0].text)
                        casefile.execution_results.append(WorkflowExecutionResult(**result_dict))
                        self._casefile_manager.db_manager.save_casefile(casefile)
                        logger.info(f"Orchestrator: Successfully saved execution result to casefile '{casefile_id}'.")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Execution of workflow {workflow_to_execute.workflow_id} simulated. Results are saved.")]))
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Orchestrator: Failed to decode or save execution result. Error: {e}")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error processing result from ExecutorAgent: {e}")]))
                else:
                    yield event
            return

        # 3. "Execution to Analysis" Workflow
        elif casefile.execution_results and not casefile.engineered_workflows:
            logger.info(f"Orchestrator: Casefile '{casefile_id}' has results. Delegating to EngineerAgent for analysis.")

            # Create a new InvocationContext for the EngineerAgent
            engineer_session = await ctx.session_service.create_session(
                app_name=ctx.session.app_name,
                user_id=ctx.session.user_id,
                state={"query": "Analyze the mission, the executed workflow, and the results to design a new, optimized, and reusable EngineeredWorkflow.", "casefile_id": casefile_id}
            )
            engineer_ctx = InvocationContext(
                session=engineer_session,
                session_service=ctx.session_service,
                invocation_id=str(uuid.uuid4()),
                agent=self._engineer_agent
            )
            async for event in self._engineer_agent._run_async_impl(engineer_ctx):
                if event.is_final_response():
                    try:
                        eng_workflow_dict = json.loads(event.content.parts[0].text)
                        casefile.engineered_workflows.append(EngineeredWorkflow(**eng_workflow_dict))
                        self._casefile_manager.db_manager.save_casefile(casefile)
                        logger.info(f"Orchestrator: Successfully saved new EngineeredWorkflow to casefile '{casefile_id}'.")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Analysis complete. An optimized workflow has been engineered and saved.")]))
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Orchestrator: Failed to decode or save engineered workflow. Error: {e}")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error processing analysis from EngineerAgent: {e}")]))
                else:
                    yield event
            return

        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Orchestrator: No immediate action required.")]))
