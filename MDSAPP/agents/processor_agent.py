# MDSAPP/agents/processor_agent.py

import logging
import json
from typing import AsyncGenerator

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import Workflow

logger = logging.getLogger(__name__)

class ProcessorAgent(BaseAgent):
    """
    Specialist agent that creates a `Workflow` object from a mission brief.
    Refactored to use the ADK's LlmAgent for core logic.
    """
    _llm_agent: LlmAgent = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        model_name: str,
        prompt_manager: PromptManager,
        retriever: any, # Retriever is unused, but kept for signature consistency
        tool_registry: ToolRegistry,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._prompt_manager = prompt_manager
        self._tool_registry = tool_registry

        self._llm_agent = LlmAgent(
            name=f"{name}_LlmImpl",
            model=model_name,
            instruction="{{system_instruction}}",
            # The ProcessorAgent's job is to generate a JSON workflow,
            # so it does not have callable tools. It receives them as context.
            tools=[],
            output_key="final_response",
        )
        self.sub_agents = [self._llm_agent]
        logger.info(f"ProcessorAgent initialized with model: {model_name}")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Prepares the context for the LlmAgent by rendering a dynamic prompt
        with the mission, available tools, and the required JSON schema.
        """
        mission = ctx.session.state.get("mission", "")
        if not mission:
            yield Event(author=self.name, content="Error: Mission not found in session state.")
            return

        logger.info(f"ProcessorAgent: Preparing context for mission: {mission[:50]}...")

        # 1. Get the prompt template
        prompt_config = self._prompt_manager.get_prompt_definition("PROCESSOR")
        if not prompt_config:
            yield Event(author=self.name, content="Error: Could not retrieve PROCESSOR prompt.")
            return

        # 2. Get available tools to provide them as context to the LLM
        tool_declarations = self._tool_registry.get_all_tool_declarations()
        tools_json_str = json.dumps([t for t in tool_declarations], indent=2)

        # 3. Format the prompt with the mission and available tools
        system_instruction = prompt_config.system_prompt.format(
            mission=mission,
            available_tools=tools_json_str,
            json_schema=Workflow.model_json_schema()
        )

        # 4. Place the dynamic instruction into the session state for the LlmAgent
        ctx.session.state["system_instruction"] = system_instruction
        logger.info("[ProcessorAgent] Placed dynamic system instruction into session state.")

        # 5. Delegate to the internal LlmAgent
        logger.info("[ProcessorAgent] Invoking the wrapped LlmAgent...")
        async for event in self._llm_agent.run_async(ctx):
            # The LlmAgent will now handle the LLM call and JSON parsing.
            # The final response will be in the event with author=self._llm_agent.name
            yield event
        logger.info("[ProcessorAgent] Orchestration turn complete.")
