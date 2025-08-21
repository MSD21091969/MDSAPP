# MDSAPP/CommunicationsManagement/manager.py

import logging
import datetime
import uuid
from typing import Any, Dict, Optional
import json # Added for structured logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Imports will be updated to point to new MDSAPP locations
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.WorkFlowManagement.manager import WorkflowManager
# 
from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.agents.chat_agent import ChatAgent # Updated import
from MDSAPP.agents.engineer_agent import EngineerAgent
from MDSAPP.core.logging.adk_logging_plugin import MdsLoggingPlugin
from MDSAPP.core.models.conversation_session import ConversationSession, Message

# Import new Command models
from MDSAPP.core.models.commands import Command, CommandStatus, CreateCasefileCommand, UpdateCasefileCommand, DeleteCasefileCommand, LogEventCommand, RunEngineerAgentCommand

logger = logging.getLogger(__name__)

class CommunicationManager:
    """
    The central communication bus for the MDS application. It handles all
    inbound and outbound communication, logging, tracing, and delegation
    to other specialized managers.
    """
    def __init__(
        self,
        db_manager: DatabaseManager,
        casefile_manager: CasefileManager,
        workflow_manager: WorkflowManager,
        prompt_manager: PromptManager,
        chat_agent: Optional[ChatAgent] = None, # Made optional to break circular dependency
        engineer_agent: Optional[EngineerAgent] = None,
        # We will add other agents and services as dependencies here
    ):
        self.db_manager = db_manager
        self.casefile_manager = casefile_manager
        self.workflow_manager = workflow_manager
        self.prompt_manager = prompt_manager
        self.chat_agent = chat_agent
        self.engineer_agent = engineer_agent
        logger.info("CommunicationManager (v2) initialized.")

    def set_chat_agent(self, chat_agent: "ChatAgent"):
        self.chat_agent = chat_agent

    async def dispatch(self, command: Command) -> Command:
        """
        Dispatches a command to the appropriate manager, logging its lifecycle.
        This is the central control point for all state-changing operations.
        """
        command.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        command.status = CommandStatus.RECEIVED
        self.log_communication(f"Dispatching command: {command.command_type}", "COMMAND_DISPATCH", command.model_dump())

        try:
            result = None
            user_id = command.user_id

            if command.command_type == "CREATE_CASEFILE":
                cmd = CreateCasefileCommand(**command.model_dump())
                result = await self.casefile_manager.create_casefile(user_id=user_id, **cmd.payload)
            elif command.command_type == "UPDATE_CASEFILE":
                cmd = UpdateCasefileCommand(**command.model_dump())
                casefile_id = cmd.payload.pop("casefile_id")
                result = await self.casefile_manager.update_casefile(casefile_id=casefile_id, user_id=user_id, updates=cmd.payload)
            elif command.command_type == "DELETE_CASEFILE":
                cmd = DeleteCasefileCommand(**command.model_dump())
                # Assuming delete_casefile will also need a permission check
                result = await self.casefile_manager.delete_casefile(user_id=user_id, **cmd.payload)
            elif command.command_type == "LOG_EVENT":
                cmd = LogEventCommand(**command.model_dump())
                result = await self.casefile_manager.log_event(user_id=user_id, **cmd.payload)
            elif command.command_type == "RUN_ENGINEER_AGENT":
                cmd = RunEngineerAgentCommand(**command.model_dump())
                query = cmd.payload.get("query")
                casefile_id = cmd.payload.get("casefile_id")
                task_type = cmd.payload.get("task_type")
                result = await self._run_engineer_agent(query=query, casefile_id=casefile_id, user_id=user_id, task_type=task_type)
            # Add more command types for other managers here
            else:
                raise ValueError(f"Unknown command type: {command.command_type}")

            command.status = CommandStatus.COMPLETED
            command.result = result.model_dump() if hasattr(result, 'model_dump') else result
            self.log_communication(f"Command {command.command_type} completed successfully.", "COMMAND_DISPATCH", command.model_dump())
            return command

        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error = str(e)
            self.log_communication(f"Command {command.command_type} failed: {e}", "COMMAND_DISPATCH", command.model_dump(), level=logging.ERROR)
            raise

    async def handle_user_request(self, user_input: str, casefile_id: str, user_id: str) -> Dict[str, Any]:
        """
        Handles a request from an external user, acting as the
        single point of entry for user interactions.
        """
        # 1. Log the incoming request using a centralized method
        self.log_communication(f"Received user request for casefile '{casefile_id}'", "EXTERNAL_IN", {"user_input": user_input})

        # 2. Delegate to the CasefileManager to log the event to the casefile's permanent record
        # Now using the dispatch method for logging events
        log_user_event_command = LogEventCommand(
            command_id=str(uuid.uuid4()),
            source_agent="USER_INTERFACE", # Source is the UI for direct user input
            user_id=user_id,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            payload={
                "casefile_id": casefile_id,
                "source": "USER",
                "event_type": "USER_MESSAGE",
                "content": user_input
            }
        )
        await self.dispatch(log_user_event_command)

        # 3. Orchestrate the chat agent to generate a response
        response_text = await self._run_chat_agent(user_input, casefile_id, user_id)

        # 4. Log the outgoing response
        self.log_communication(f"Sending response for casefile '{casefile_id}'", "EXTERNAL_OUT", {"response": response_text})
        
        # 5. Delegate to the CasefileManager to log the agent's response
        # Now using the dispatch method for logging events
        log_agent_event_command = LogEventCommand(
            command_id=str(uuid.uuid4()),
            source_agent="COMMUNICATION_MANAGER", # Source is the CommunicationManager dispatching on behalf of ChatAgent
            user_id=user_id,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            payload={
                "casefile_id": casefile_id,
                "source": "CHAT_AGENT",
                "event_type": "AGENT_MESSAGE",
                "content": response_text
            }
        )
        await self.dispatch(log_agent_event_command)

        return {"response": response_text, "casefile_id": casefile_id}

    def log_communication(self, message: str, direction: str, payload: Dict = None, level: int = logging.INFO):
        """A centralized method for logging all communication events."""
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "direction": direction,
            "message": message,
            "payload": payload or {}
        }
        if level == logging.ERROR:
            logger.error(f"COMMUNICATION_LOG :: {json.dumps(log_entry)}")
        else:
            logger.info(f"COMMUNICATION_LOG :: {json.dumps(log_entry)}")

    async def _run_engineer_agent(self, query: str, casefile_id: str, user_id: str, task_type: str) -> str:
        """Private method to contain the ADK runner logic for the engineer agent."""
        logger.info(f"Orchestrating Engineer Agent for task: {task_type}...")

        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.engineer_agent,
            app_name="mds7_engineer_comm_manager",
            session_service=session_service,
            plugins=[MdsLoggingPlugin()],
        )

        initial_state = {
            "query": query,
            "casefile_id": casefile_id,
            "user_id": user_id,
            "task_type": task_type,
        }
        
        session_id = f"session-comm-eng-{uuid.uuid4().hex}"
        session = await session_service.create_session(
            app_name="mds7_engineer_comm_manager", user_id=user_id, session_id=session_id, state=initial_state
        )

        user_message = genai_types.Content(role='user', parts=[genai_types.Part(text=query)])

        final_response = "Error: No response from engineer agent."
        async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=user_message):
            if event.is_final_response():
                final_response = event.content.parts[0].text
        
        return final_response

    async def _run_chat_agent(self, user_input: str, casefile_id: str, user_id: str) -> str:
        """Private method to contain the ADK runner logic for the chat agent.
        NOTE: With the ChatAgent refactoring to use a standard LlmAgent,
        the conversation history is now managed by the ADK's session service.
        The previous manual persistence via ConversationSession has been removed.
        History is now in-memory for the duration of the session.
        """
        logger.info("Orchestrating Chat Agent via ADK Runner...")

        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.chat_agent,
            app_name="mds7_chat_comm_manager",  # Unique app name for this runner
            session_service=session_service,
            plugins=[MdsLoggingPlugin()],
        )

        # Use a consistent session ID to maintain conversation history in memory
        session_id = f"conv-{user_id}-{casefile_id}"

        # The new ChatAgent only needs user_input and casefile_id in the state
        # for the first turn to prepare the dynamic prompt.
        initial_state = {
            "user_input": user_input,
            "casefile_id": casefile_id,
            "user_id": user_id,
        }

        # The runner will create the session if it doesn't exist.
        session = await session_service.get_session(app_name="mds7_chat_comm_manager", user_id=user_id, session_id=session_id)
        if not session:
            session = await session_service.create_session(
                app_name="mds7_chat_comm_manager", user_id=user_id, session_id=session_id, state=initial_state
            )
        else:
            # Update state for the new turn
            session.state["user_input"] = user_input
            session.state["casefile_id"] = casefile_id

        user_message = genai_types.Content(role='user', parts=[genai_types.Part(text=user_input)])
        
        final_response = "Error: No response from agent."
        # The LlmAgent will yield its own final response event.
        async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=user_message):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        # The session state is managed by the InMemorySessionService now.
        # Manual persistence is removed for now.
        
        return final_response
