# MDSAPP/agents/chat_agent.py

import logging
from typing import AsyncGenerator, Any

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from MDSAPP.CasefileManagement.models.casefile import Casefile

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ChatAgent(BaseAgent):
    """
    Orchestrator for the chat experience.

    This agent is responsible for preparing the context for the chat,
    including rendering a dynamic system prompt based on the current casefile.
    It then delegates the core chat logic, including history and tool use,
    to a standard LlmAgent. This pattern is inspired by the ADK examples.
    """
    _llm_agent: LlmAgent = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _casefile_manager: CasefileManager = PrivateAttr()

    def __init__(
        self,
        name: str,
        model_name: str,
        prompt_manager: PromptManager,
        retriever: Any,
        casefile_manager: CasefileManager,
        drive_manager: Any,
        tool_registry: ToolRegistry,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self._prompt_manager = prompt_manager
        self._casefile_manager = casefile_manager

        # FIX: Pass the callable tool handlers directly to the LlmAgent.
        # The ADK will introspect these callables to generate tool schemas.
        tool_handlers = list(tool_registry._tool_handlers.values())

        self._llm_agent = LlmAgent(
            name=f"{name}_LlmImpl",
            model=model_name,
            instruction="{{system_instruction}}",
            tools=tool_handlers,
            output_key="final_response",
        )

        self.sub_agents = [self._llm_agent]
        logger.info("ChatAgent orchestrator initialized with internal LlmAgent.")

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the standard "wrapper" pattern for orchestrating a sub-agent
        based on the official ADK documentation.

        This method prepares the necessary context by placing a dynamic prompt
        into the session state, and then invokes the internal LlmAgent.
        """
        casefile_id = ctx.session.state.get("casefile_id", "")
        logger.info(f"[ChatAgent] Orchestrator started for casefile: {casefile_id}")

        # 1. Get the user input from the context's `user_content` attribute.
        # This is based on the user's trace file.
        if not ctx.user_content or not ctx.user_content.parts:
            logger.warning("[ChatAgent] No user_content found in the context.")
            return
        user_input = ctx.user_content.parts[0].text
        logger.info(f"[ChatAgent] Input from user_content: '{user_input}'")

        # 2. Load the casefile to get context for the dynamic prompt.
        casefile = None
        if casefile_id:
            casefile_json = await self._casefile_manager.load_casefile(casefile_id)
            if casefile_json:
                casefile = Casefile.model_validate_json(casefile_json)

        # 3. Render the dynamic system instruction for the LlmAgent.
        await self._prompt_manager.load_prompts_from_db()
        system_instruction = self._prompt_manager.render_prompt(
            agent_name="ChatAgent",
            task_name="chat",
            context={"casefile": casefile},
        )
        if not system_instruction:
            system_instruction = "You are a helpful assistant."  # Fallback

        # 4. Place the dynamic instruction into the session state.
        # The LlmAgent is configured with instruction="{{system_instruction}}"
        # and will read this value from the state.
        ctx.session.state["system_instruction"] = system_instruction
        logger.info("[ChatAgent] Placed dynamic system instruction into session state.")

        # 5. Delegate to the LlmAgent using the original context.
        # The LlmAgent will automatically access the latest user_content and the
        # full conversation history from the context provided by the runner.
        logger.info("[ChatAgent] Invoking the wrapped LlmAgent...")
        async for event in self._llm_agent.run_async(ctx):
            yield event

        logger.info("[ChatAgent] Orchestration turn complete.")