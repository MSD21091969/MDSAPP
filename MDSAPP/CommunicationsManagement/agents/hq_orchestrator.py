# MDSAPP/agents/hq_orchestrator.py

import logging
import json
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

    def __init__(
        self,
        name: str,
        casefile_manager: CasefileManager,
        tool_registry: ToolRegistry,
        sub_agents: list[LlmAgent] | None = None,
        **kwargs
    ):
        super().__init__(name=name, sub_agents=sub_agents, **kwargs)
        self._casefile_manager = casefile_manager
        self._tool_registry = tool_registry
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

        casefile = self._casefile_manager.load_casefile(casefile_id)
        if not casefile:
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error: Casefile {casefile_id} not found.")]))
            return

        # --- Orchestration Logic --- #

        # 1. "Mission to Plan" Workflow
        if casefile.mission and not casefile.workflows:
            logger.info(f"Orchestrator: Casefile '{casefile_id}' requires a plan. Delegating to ProcessorAgent.")
            processor_tool: AgentTool = self._tool_registry.get_tool_handler("run_processor_agent")
            if not processor_tool:
                yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Error: ProcessorAgent tool not found.")]))
                return
            ctx.session.state["mission"] = casefile.mission
            async for event in processor_tool.run_async(ctx):
                if event.is_final_response():
                    try:
                        workflow_dict = json.loads(event.content.parts[0].text)
                        casefile.workflows.append(Workflow(**workflow_dict))
                        self._casefile_manager.save_casefile(casefile)
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
            executor_tool: AgentTool = self._tool_registry.get_tool_handler("run_executor_agent")
            if not executor_tool:
                yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Error: ExecutorAgent tool not found.")]))
                return
            workflow_to_execute = casefile.workflows[0]
            ctx.session.state["workflow"] = workflow_to_execute.model_dump()
            async for event in executor_tool.run_async(ctx):
                if event.is_final_response():
                    try:
                        result_dict = json.loads(event.content.parts[0].text)
                        casefile.execution_results.append(WorkflowExecutionResult(**result_dict))
                        self._casefile_manager.save_casefile(casefile)
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
            engineer_tool: AgentTool = self._tool_registry.get_tool_handler("run_engineer_agent")
            if not engineer_tool:
                yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Error: EngineerAgent tool not found.")]))
                return
            ctx.session.state["query"] = "Analyze the mission, the executed workflow, and the results to design a new, optimized, and reusable EngineeredWorkflow."
            async for event in engineer_tool.run_async(ctx):
                if event.is_final_response():
                    try:
                        eng_workflow_dict = json.loads(event.content.parts[0].text)
                        casefile.engineered_workflows.append(EngineeredWorkflow(**eng_workflow_dict))
                        self._casefile_manager.save_casefile(casefile)
                        logger.info(f"Orchestrator: Successfully saved new EngineeredWorkflow to casefile '{casefile_id}'.")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Analysis complete. An optimized workflow has been engineered and saved.")]))
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Orchestrator: Failed to decode or save engineered workflow. Error: {e}")
                        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=f"Error processing analysis from EngineerAgent: {e}")]))
                else:
                    yield event
            return

        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Orchestrator: No immediate action required.")]))
