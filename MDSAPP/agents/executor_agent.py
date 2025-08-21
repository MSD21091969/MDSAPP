# MDSAPP/agents/executor_agent.py

import logging
import json
import datetime
from typing import AsyncGenerator, Dict, Any

from typing_extensions import override
from pydantic import PrivateAttr, ValidationError

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types

from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import Workflow, ElementType
from MDSAPP.WorkFlowManagement.models.results import WorkflowExecutionResult, StepResult, StepStatus
from MDSAPP.core.models.ontology import WorkflowStatus # Added import

logger = logging.getLogger(__name__)

class ExecutorAgent(BaseAgent):
    """
    Specialist agent that executes a given `Workflow` by interpreting its
    elements and calling the required tools step-by-step.
    """
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        tool_registry: ToolRegistry,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._tool_registry = tool_registry
        logger.info(f"ExecutorAgent (v2) initialized.")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        The core logic for the ExecutorAgent. It executes a workflow step-by-step.
        """
        workflow_dict = ctx.session.state.get("workflow", {})
        if not workflow_dict:
            yield Event(author=self.name, content="Error: Workflow not found in session state.")
            return

        try:
            workflow = Workflow(**workflow_dict)
            logger.info(f"Executor starting execution for workflow: {workflow.workflow_id}")
        except ValidationError as e:
            yield Event(author=self.name, content=f"Error: Invalid workflow structure provided. Details: {e}")
            return

        step_results: list[StepResult] = []
        start_time = datetime.datetime.now(datetime.timezone.utc)

        # For now, we assume a simple sequential execution of all tool elements
        for element in workflow.elements:
            if element.type == ElementType.TOOL:
                tool_name = element.metadata.get("tool_name")
                tool_args = element.metadata.get("arguments", {})
                step_start_time = datetime.datetime.now(datetime.timezone.utc)

                if not tool_name:
                    logger.warning(f"Element '{element.id}' is a tool but has no tool_name in metadata.")
                    continue

                handler = self._tool_registry.get_tool_handler(tool_name)
                if not handler:
                    step_results.append(StepResult(
                        element_id=element.id,
                        status=StepStatus.FAILED,
                        output={"error": f"Tool '{tool_name}' not found in registry."},
                        started_at=step_start_time,
                        ended_at=datetime.datetime.now(datetime.timezone.utc)
                    ))
                    continue
                
                try:
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    # Note: This assumes all tools are synchronous for now.
                    # For async tools, we would need to `await handler(**tool_args)`
                    result = handler(**tool_args)
                    step_results.append(StepResult(
                        element_id=element.id,
                        status=StepStatus.COMPLETED,
                        output=result,
                        started_at=step_start_time,
                        ended_at=datetime.datetime.now(datetime.timezone.utc)
                    ))
                except Exception as e:
                    logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
                    step_results.append(StepResult(
                        element_id=element.id,
                        status=StepStatus.FAILED,
                        output={"error": str(e)},
                        started_at=step_start_time,
                        ended_at=datetime.datetime.now(datetime.timezone.utc)
                    ))

        # Compile final result
        final_result = WorkflowExecutionResult(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.COMPLETED, # Or FAILED if any step failed
            steps=step_results,
            started_at=start_time,
            ended_at=datetime.datetime.now(datetime.timezone.utc)
        )

        final_json_string = final_result.model_dump_json()
        logger.info(f"Finished execution for workflow: {workflow.workflow_id}")

        yield Event(
            author=self.name,
            content=genai_types.Content(role="model", parts=[genai_types.Part(text=final_json_string)])
        )
