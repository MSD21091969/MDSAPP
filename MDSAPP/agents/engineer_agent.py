# MDSAPP/agents/engineer_agent.py

import logging
import json
from typing import AsyncGenerator

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import EngineeredWorkflow
from MDSAPP.core.tools.research_tools import google_web_search

logger = logging.getLogger(__name__)

class EngineerAgent(BaseAgent):
    """
    Specialist meta-agent that analyzes results and creates optimized `EngineeredWorkflow` templates.
    Refactored to use the ADK's LlmAgent for core logic.
    """
    _llm_agent: LlmAgent = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _casefile_manager: CasefileManager = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        model_name: str,
        prompt_manager: PromptManager,
        casefile_manager: CasefileManager,
        tool_registry: ToolRegistry,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._prompt_manager = prompt_manager
        self._casefile_manager = casefile_manager
        self._tool_registry = tool_registry

        # The EngineerAgent has its own tools, which we pass to the LlmAgent.
        tools = [self.produce_dataset, google_web_search]

        self._llm_agent = LlmAgent(
            name=f"{name}_LlmImpl",
            model=model_name,
            instruction="{{system_instruction}}",
            tools=tools,
            output_key="final_response",
        )
        self.sub_agents = [self._llm_agent]
        logger.info(f"EngineerAgent initialized with model: {model_name}")

    async def produce_dataset(self, casefile_id: str) -> str:
        """
        Placeholder for logic to produce a dataset for the specified casefile.
        """
        logger.info(f"EngineerAgent: Initiating dataset production for casefile: {casefile_id}")
        # In a real implementation, this would involve complex logic.
        return f"Dataset production initiated for casefile {casefile_id}."

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Prepares the context for the LlmAgent by determining the task
        (research or workflow engineering) and rendering the appropriate prompt.
        """
        casefile_id = ctx.session.state.get("casefile_id", "")
        task_type = ctx.session.state.get("task_type", "workflow_engineering")
        query = ctx.session.state.get("query", "")

        if not casefile_id:
            yield Event(author=self.name, content="Error: casefile_id is required.")
            return

        if task_type == "research":
            system_instruction = await self._prepare_research_prompt(query)
        else: # workflow_engineering
            system_instruction = await self._prepare_workflow_engineering_prompt(casefile_id)

        if not system_instruction:
            # If prompt preparation failed, yield an error event.
            yield Event(author=self.name, content="Error: Could not prepare system instruction for the task.")
            return

        ctx.session.state["system_instruction"] = system_instruction
        logger.info(f"[EngineerAgent] Placed dynamic system instruction for task: {task_type}")

        logger.info("[EngineerAgent] Invoking the wrapped LlmAgent...")
        async for event in self._llm_agent.run_async(ctx):
            yield event
        logger.info("[EngineerAgent] Orchestration turn complete.")

    async def _prepare_research_prompt(self, query: str) -> str | None:
        logger.info(f"EngineerAgent: Preparing research prompt for query: '{query}'")
        prompt_config = self._prompt_manager.get_prompt_definition("ENGINEER_RESEARCH")
        if not prompt_config:
            logger.error("Could not retrieve ENGINEER_RESEARCH prompt.")
            return None
        
        # The LlmAgent will get the tools directly, so we don't need to pass them in the prompt.
        return prompt_config.system_prompt.format(query=query)

    async def _prepare_workflow_engineering_prompt(self, casefile_id: str) -> str | None:
        casefile = await self._casefile_manager.load_casefile(casefile_id)
        if not casefile:
            logger.error(f"Casefile with ID '{casefile_id}' not found.")
            return None

        if not casefile.workflows or not casefile.execution_results:
            logger.error(f"Casefile '{casefile_id}' lacks a workflow and/or results to engineer.")
            return None

        logger.info(f"EngineerAgent: Preparing workflow engineering prompt for casefile: {casefile_id}")
        prompt_config = self._prompt_manager.get_prompt_definition("ENGINEER")
        if not prompt_config:
            logger.error("Could not retrieve ENGINEER prompt.")
            return None

        original_workflow = casefile.workflows[0].model_dump_json(indent=2)
        execution_results = casefile.execution_results[0].model_dump_json(indent=2)
        
        # The LlmAgent gets tools directly. We provide the schema in the prompt.
        tool_declarations = self._tool_registry.get_all_tool_declarations()
        tools_json_str = json.dumps([t for t in tool_declarations], indent=2)

        return prompt_config.system_prompt.format(
            mission=casefile.campaign,
            original_workflow=original_workflow,
            execution_results=execution_results,
            available_tools=tools_json_str,
            json_schema=EngineeredWorkflow.model_json_schema()
        )
