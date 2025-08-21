# MDSAPP/core/logging/adk_logging_plugin.py

import logging
from typing import Any, Optional

from google.genai import types

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class MdsLoggingPlugin(BasePlugin):
    """A plugin that logs ADK events to a structured logger."""

    def __init__(self, name: str = "mds_logging_plugin"):
        super().__init__(name)

    async def on_user_message_callback(
        self,
        *,
        invocation_context: InvocationContext,
        user_message: types.Content,
    ) -> Optional[types.Content]:
        log_data = {
            "event": "on_user_message_callback",
            "invocation_id": invocation_context.invocation_id,
            "session_id": invocation_context.session.id,
            "user_id": invocation_context.user_id,
            "app_name": invocation_context.app_name,
            "root_agent": getattr(invocation_context.agent, 'name', 'Unknown'),
            "user_content": self._format_content(user_message),
            "branch": invocation_context.branch,
        }
        logger.info(log_data)
        return None

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[types.Content]:
        log_data = {
            "event": "before_run_callback",
            "invocation_id": invocation_context.invocation_id,
            "starting_agent": getattr(invocation_context.agent, 'name', 'Unknown'),
        }
        logger.info(log_data)
        return None

    async def on_event_callback(
        self, *, invocation_context: InvocationContext, event: Event
    ) -> Optional[Event]:
        log_data = {
            "event": "on_event_callback",
            "event_id": event.id,
            "author": event.author,
            "content": self._format_content(event.content),
            "is_final_response": event.is_final_response(),
            "function_calls": [fc.name for fc in event.get_function_calls()],
            "function_responses": [fr.name for fr in event.get_function_responses()],
            "long_running_tool_ids": list(event.long_running_tool_ids or []),
        }
        logger.info(log_data)
        return None

    async def after_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[None]:
        log_data = {
            "event": "after_run_callback",
            "invocation_id": invocation_context.invocation_id,
            "final_agent": getattr(invocation_context.agent, 'name', 'Unknown'),
        }
        logger.info(log_data)
        return None

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        log_data = {
            "event": "before_agent_callback",
            "agent_name": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
            "branch": callback_context._invocation_context.branch,
        }
        logger.info(log_data)
        return None

    async def after_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        log_data = {
            "event": "after_agent_callback",
            "agent_name": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
        }
        logger.info(log_data)
        return None

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        log_data = {
            "event": "before_model_callback",
            "model": llm_request.model or 'default',
            "agent": callback_context.agent_name,
            "available_tools": list(llm_request.tools_dict.keys()) if llm_request.tools_dict else [],
        }
        logger.info(log_data)
        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        log_data = {
            "event": "after_model_callback",
            "agent": callback_context.agent_name,
            "error_code": llm_response.error_code,
            "error_message": llm_response.error_message,
            "content": self._format_content(llm_response.content),
            "partial": llm_response.partial,
            "turn_complete": llm_response.turn_complete,
            "token_usage_input": llm_response.usage_metadata.prompt_token_count if llm_response.usage_metadata else None,
            "token_usage_output": llm_response.usage_metadata.candidates_token_count if llm_response.usage_metadata else None,
        }
        logger.info(log_data)
        return None

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext
    ) -> Optional[dict]:
        log_data = {
            "event": "before_tool_callback",
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "function_call_id": tool_context.function_call_id,
            "arguments": self._format_args(tool_args),
        }
        logger.info(log_data)
        return None

    async def after_tool_callback(
        self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext, result: dict
    ) -> Optional[dict]:
        log_data = {
            "event": "after_tool_callback",
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "function_call_id": tool_context.function_call_id,
            "result": self._format_args(result),
        }
        logger.info(log_data)
        return None

    async def on_model_error_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest, error: Exception
    ) -> Optional[LlmResponse]:
        log_data = {
            "event": "on_model_error_callback",
            "agent": callback_context.agent_name,
            "error": str(error),
        }
        logger.error(log_data)
        return None

    async def on_tool_error_callback(
        self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext, error: Exception
    ) -> Optional[dict]:
        log_data = {
            "event": "on_tool_error_callback",
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "function_call_id": tool_context.function_call_id,
            "arguments": self._format_args(tool_args),
            "error": str(error),
        }
        logger.error(log_data)
        return None

    def _format_content(
        self, content: Optional[types.Content], max_length: int = 200
    ) -> str:
        if not content or not content.parts:
            return "None"
        # Omitting detailed content formatting for brevity in this example
        return f"{len(content.parts)} part(s)"

    def _format_args(self, args: dict[str, Any], max_length: int = 300) -> str:
        if not args:
            return "{}"
        formatted = str(args)
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "...}"
        return formatted
