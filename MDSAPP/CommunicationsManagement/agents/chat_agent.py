# MDSAPP/CommunicationsManagement/agents/chat_agent.py

import logging
import json
from typing import AsyncGenerator, Any, Dict

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.core.services.retriever import Retriever
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.services.drive_manager import DriveManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.CommunicationsManagement.manager import CommunicationManager

logger = logging.getLogger(__name__)

class ChatAgent(BaseAgent):
    """
    Specialist agent for user-facing conversational interactions.
    This agent has been refactored to use the ADK's LlmAgent for core logic,
    while preserving its role in preparing context and potentially interacting
    with the CommunicationManager in the future.
    """
    _llm_agent: LlmAgent = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _retriever: Retriever = PrivateAttr()
    _comm_manager: CommunicationManager = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        model_name: str,
        prompt_manager: PromptManager,
        retriever: Retriever,
        casefile_manager: CasefileManager,
        drive_manager: DriveManager,
        tool_registry: ToolRegistry,
        comm_manager: CommunicationManager,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._prompt_manager = prompt_manager
        self._retriever = retriever
        self._comm_manager = comm_manager
        self._tool_registry = tool_registry

        tool_handlers = list(self._tool_registry._tool_handlers.values())

        # TODO: The command bus logic needs to be refactored directly into the
        # tool handlers. For now, the tools will be called directly by the ADK.
        # This involves creating wrapper functions for critical tools that
        # dispatch commands via self._comm_manager instead of executing directly.
        logger.warning(
            "The command bus logic in the CommunicationsManagement.ChatAgent "
            "is temporarily bypassed. Tools will be executed directly."
        )

        self._llm_agent = LlmAgent(
            name=f"{name}_LlmImpl",
            model=model_name,
            instruction="{{system_instruction}}",
            tools=tool_handlers,
            output_key="final_response",
        )
        self.sub_agents = [self._llm_agent]
        logger.info(f"ChatAgent initialized with model: {model_name}")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Prepares the context for the LlmAgent by retrieving relevant information
        and rendering a dynamic prompt.
        """
        user_input = ctx.session.state.get("user_input", "")
        casefile_id = ctx.session.state.get("casefile_id", "")

        # 1. Retrieve context for the current query
        retrieved_context = self._retriever.retrieve(query=user_input, casefile_id=casefile_id)

        # 2. Render a dynamic system instruction for the LlmAgent
        # Note: This prompt could be enhanced in PromptManager to include the retrieved_context
        system_instruction = self._prompt_manager.render_prompt(
            agent_name="CommunicationsManagement.ChatAgent",
            task_name="chat",
            context={"retrieved_context": retrieved_context, "user_input": user_input}
        )
        if not system_instruction:
            # Fallback prompt that includes the retrieved context
            system_instruction = f"""You are a helpful assistant. Use the following retrieved context to answer the user's query.
--- CONTEXT ---
{retrieved_context}
--- END CONTEXT ---"""

        # 3. Place the dynamic instruction into the session state for the LlmAgent
        ctx.session.state["system_instruction"] = system_instruction
        logger.info("[Comm.ChatAgent] Placed dynamic system instruction into session state.")

        # 4. Delegate to the internal LlmAgent
        logger.info("[Comm.ChatAgent] Invoking the wrapped LlmAgent...")
        async for event in self._llm_agent.run_async(ctx):
            yield event
        logger.info("[Comm.ChatAgent] Orchestration turn complete.")