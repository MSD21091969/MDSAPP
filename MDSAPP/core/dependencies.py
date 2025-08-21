# MDSAPP/core/dependencies.py

import logging
from functools import lru_cache
import os

# ADK will handle initialization based on environment variables.
# No direct imports from vertexai or google.generativeai are needed here.

from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool
from google.genai.types import FunctionDeclaration # This is ok for tool declaration

# Import Agents
# Correctly import the refactored ChatAgent
from MDSAPP.agents.chat_agent import ChatAgent as HighLevelChatAgent
from MDSAPP.CommunicationsManagement.agents.chat_agent import ChatAgent as CommsChatAgent
from MDSAPP.agents.processor_agent import ProcessorAgent
from MDSAPP.agents.executor_agent import ExecutorAgent
from MDSAPP.agents.engineer_agent import EngineerAgent
from MDSAPP.agents.hq_orchestrator import HQOrchestratorAgent

# Import Managers
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.CommunicationsManagement.manager import CommunicationManager
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.core.managers.embeddings_manager import EmbeddingsManager
from MDSAPP.WorkFlowManagement.manager import WorkflowManager

# Import Services & Utils
from MDSAPP.core.services.drive_manager import DriveManager
from MDSAPP.core.services.retriever import Retriever
from MDSAPP.core.services.firestore_retriever import FirestoreRetriever
from MDSAPP.core.utils.document_parser import DocumentParser
from MDSAPP.core.services.google_workspace_manager import GoogleWorkspaceManager
from MDSAPP.core.services.google_api_mock import MockGoogleDriveService
from MDSAPP.core.utils.data_generator import generate_real_estate_dossier

# Import Tools
from MDSAPP.core.tools.real_estate_tools import get_kadaster_info
from MDSAPP.core.tools.analysis_tools import calculate_execution_summary

logger = logging.getLogger(__name__)

# Define the model name as a constant to ensure consistency
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# This function will be called by main.py to set up all tools
def register_all_tools(tool_registry: ToolRegistry):
    logger.info("--- Starting Tool Registration ---")

    # --- Register System Tools ---
    def log_message(message: str):
        """A simple tool to log a message to the console."""
        logger.info(f"TOOL_LOG: {message}")
        return {"status": "SUCCESS", "message": message}

    log_message_declaration = FunctionDeclaration(
        name="log_message",
        description="Logs a message to the system log. Used for debugging and simple workflow steps.",
        parameters={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
    )
    tool_registry.register_tool("log_message", log_message_declaration, log_message)
    logger.info("log_message registered as a tool.")

    # Register Manager-based tools
    get_casefile_manager().register_tools(tool_registry)
    get_google_workspace_manager().register_tools(tool_registry)

    # --- Register EngineerAgent ---
    engineer_agent = get_engineer_agent()
    engineer_tool_declaration = FunctionDeclaration(
        name="run_engineer_agent",
        description="Tool for advanced data analysis, logic, and interfacing with the workflow system.",
        parameters={
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "enum": ["research", "workflow_engineering"]},
                "query": {"type": "string"},
                "casefile_id": {"type": "string"}
            },
            "required": ["task_type", "casefile_id"]
        },
    )
    tool_registry.register_tool("run_engineer_agent", engineer_tool_declaration, AgentTool(agent=engineer_agent))
    logger.info("EngineerAgent registered as a tool.")

    # --- Register ProcessorAgent ---
    processor_agent = get_processor_agent()
    processor_tool_declaration = FunctionDeclaration(
        name="run_processor_agent",
        description="Tool that takes a high-level mission and creates a detailed Workflow plan.",
        parameters={"type": "object", "properties": {"mission": {"type": "string"}, "casefile_id": {"type": "string"}}, "required": ["mission", "casefile_id"]},
    )
    tool_registry.register_tool("run_processor_agent", processor_tool_declaration, AgentTool(agent=processor_agent))
    logger.info("ProcessorAgent registered as a tool.")

    # --- Register ExecutorAgent ---
    executor_agent = get_executor_agent()
    executor_tool_declaration = FunctionDeclaration(
        name="run_executor_agent",
        description="Tool that executes a given Workflow plan.",
        parameters={"type": "object", "properties": {"workflow": {"type": "object"}, "casefile_id": {"type": "string"}}, "required": ["workflow", "casefile_id"]},
    )
    tool_registry.register_tool("run_executor_agent", executor_tool_declaration, AgentTool(agent=executor_agent))
    logger.info("ExecutorAgent registered as a tool.")

    # --- Register Dossier Generator ---
    dossier_generator_declaration = FunctionDeclaration(
        name="generate_real_estate_dossier",
        description="Generates a realistic, synthetic customer dossier for the Dutch real estate market.",
        parameters={"type": "object", "properties": {"region": {"type": "string"}, "budget": {"type": "integer"}}, "required": ["region", "budget"]},
    )
    async def dossier_handler(region: str, budget: int):
        # This tool might need its own LLM call, but it should be done
        # via an ad-hoc ADK runner if needed, not by passing a model object.
        # For now, this dependency is removed to fix the core issue.
        # llm_model = get_processor_llm()
        # return await generate_real_estate_dossier(region, budget, llm_model)
        logger.warning("generate_real_estate_dossier tool is currently disabled pending refactoring.")
        return {"status": "DISABLED", "message": "This tool is pending refactoring."}

    tool_registry.register_tool("generate_real_estate_dossier", dossier_generator_declaration, dossier_handler)
    logger.info("DossierGenerator registered as a tool.")

    # --- Register HQOrchestrator ---
    hq_orchestrator = get_hq_orchestrator()
    hq_tool_declaration = FunctionDeclaration(
        name="run_hq_orchestrator",
        description="Starts the master orchestrator to manage a mission from a casefile.",
        parameters={"type": "object", "properties": {"casefile_id": {"type": "string"}}, "required": ["casefile_id"]},
    )
    tool_registry.register_tool("run_hq_orchestrator", hq_tool_declaration, AgentTool(agent=hq_orchestrator))
    logger.info("HQOrchestrator registered as a tool.")

    # --- Register Real Estate Tools ---
    kadaster_tool_declaration = FunctionDeclaration(
        name="get_kadaster_info",
        description="Retrieves official property data from the Kadaster for a specific address.",
        parameters={"type": "object", "properties": {"adres": {"type": "string"}}, "required": ["adres"]},
    )
    tool_registry.register_tool("get_kadaster_info", kadaster_tool_declaration, get_kadaster_info)
    logger.info("get_kadaster_info registered as a tool.")

    # --- Register Analysis Tools ---
    summary_tool_declaration = FunctionDeclaration(
        name="calculate_execution_summary",
        description="Calculates summary statistics from a workflow execution result.",
        parameters={"type": "object", "properties": {"execution_result": {"type": "object"}}, "required": ["execution_result"]},
    )
    tool_registry.register_tool("calculate_execution_summary", summary_tool_declaration, calculate_execution_summary)
    logger.info("calculate_execution_summary registered as a tool.")
    logger.info("--- Tool Registration Completed ---")


@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager()

@lru_cache()
def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()

@lru_cache()
def get_prompt_manager() -> PromptManager:
    logger.info("Initializing PromptManager...")
    return PromptManager(db_manager=get_database_manager())

@lru_cache()
def get_casefile_manager() -> CasefileManager:
    return CasefileManager(db_manager=get_database_manager())

@lru_cache()
def get_workflow_manager() -> WorkflowManager:
    return WorkflowManager()

@lru_cache()
def get_retriever() -> Retriever:
    return FirestoreRetriever(db_manager=get_database_manager())

@lru_cache()
def get_drive_manager() -> DriveManager:
    return DriveManager(casefile_manager=get_casefile_manager(), embeddings_manager=get_embeddings_manager())

@lru_cache()
def get_high_level_chat_agent() -> HighLevelChatAgent:
    return HighLevelChatAgent(
        name="ChatAgent",
        model_name=GEMINI_MODEL_NAME,
        prompt_manager=get_prompt_manager(),
        retriever=get_retriever(),
        casefile_manager=get_casefile_manager(),
        drive_manager=get_drive_manager(),
        tool_registry=get_tool_registry(),
    )

@lru_cache()
def get_comms_chat_agent() -> CommsChatAgent:
    return CommsChatAgent(
        name="CommsChatAgent",
        model_name=GEMINI_MODEL_NAME,
        prompt_manager=get_prompt_manager(),
        retriever=get_retriever(),
        casefile_manager=get_casefile_manager(),
        drive_manager=get_drive_manager(),
        tool_registry=get_tool_registry(),
        comm_manager=get_communication_manager(),
    )

@lru_cache()
def get_processor_agent() -> ProcessorAgent:
    # Assuming ProcessorAgent is also refactored to take model_name
    # This will need to be verified and fixed if not.
    return ProcessorAgent(
        name="ProcessorAgent",
        model_name=GEMINI_MODEL_NAME,
        prompt_manager=get_prompt_manager(),
        retriever=get_retriever(),
        tool_registry=get_tool_registry()
    )

@lru_cache()
def get_executor_agent() -> ExecutorAgent:
    return ExecutorAgent(name="ExecutorAgent", tool_registry=get_tool_registry())

@lru_cache()
def get_engineer_agent() -> EngineerAgent:
    # Assuming EngineerAgent is also refactored to take model_name
    return EngineerAgent(
        name="EngineerAgent",
        model_name=GEMINI_MODEL_NAME,
        prompt_manager=get_prompt_manager(),
        casefile_manager=get_casefile_manager(),
        tool_registry=get_tool_registry()
    )

@lru_cache()
def get_communication_manager() -> CommunicationManager:
    # Circular dependency is tricky. A common pattern is to set dependencies
    # after initialization. For now, we rely on lazy loading from the cache.
    # A more robust solution might involve a dedicated dependency injection container.
    return CommunicationManager(
        db_manager=get_database_manager(),
        casefile_manager=get_casefile_manager(),
        workflow_manager=get_workflow_manager(),
        prompt_manager=get_prompt_manager(),
    )

@lru_cache()
def get_document_parser() -> DocumentParser:
    return DocumentParser()

@lru_cache()
def get_mock_google_drive_service() -> MockGoogleDriveService:
    return MockGoogleDriveService()

@lru_cache()
def get_google_workspace_manager() -> GoogleWorkspaceManager:
    google_workspace_mgr = GoogleWorkspaceManager(
        casefile_manager=get_casefile_manager(),
        embeddings_manager=get_embeddings_manager(),
        drive_service=get_mock_google_drive_service()
    )
    get_embeddings_manager().set_google_workspace_manager(google_workspace_mgr)
    return google_workspace_mgr

@lru_cache()
def get_embeddings_manager() -> EmbeddingsManager:
    embeddings_mgr = EmbeddingsManager(
        db_manager=get_database_manager(),
        parser=get_document_parser()
    )
    return embeddings_mgr

@lru_cache()
def get_session_service() -> InMemorySessionService:
    return InMemorySessionService()

@lru_cache()
def get_hq_orchestrator() -> HQOrchestratorAgent:
    return HQOrchestratorAgent(
        name="HQOrchestratorAgent",
        casefile_manager=get_casefile_manager(),
        tool_registry=get_tool_registry(),
        processor_agent=get_processor_agent(),
        executor_agent=get_executor_agent(),
        engineer_agent=get_engineer_agent()
    )

def initialize_managers():
    logger.info("Initializing all managers...")
    # Simply call each getter to ensure they are cached.
    get_database_manager()
    get_tool_registry()
    get_prompt_manager()
    get_casefile_manager()
    get_workflow_manager()
    get_retriever()
    get_drive_manager()
    get_high_level_chat_agent()
    get_comms_chat_agent()
    get_processor_agent()
    get_executor_agent()
    get_engineer_agent()
    get_communication_manager()
    get_document_parser()
    get_mock_google_drive_service()
    get_google_workspace_manager()
    get_embeddings_manager()
    get_session_service()
    get_hq_orchestrator()

    # Break circular dependency between CommunicationManager and CommsChatAgent
    logger.info("Wiring up circular dependencies...")
    comm_manager = get_communication_manager()
    chat_agent = get_comms_chat_agent()
    comm_manager.set_chat_agent(chat_agent)
    logger.info("Circular dependencies wired up.")

    logger.info("All managers initialized.")

from fastapi import Header, HTTPException, status

def get_current_user_id(x_user_id: str = Header(None, alias="X-User-ID")) -> str:
    if x_user_id:
        return x_user_id
    
    default_user_id = os.getenv("DEFAULT_USER_ID")
    if default_user_id:
        logger.info(f"Using default user ID: {default_user_id}")
        return default_user_id
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not identify user. X-User-ID header is missing and DEFAULT_USER_ID is not set."
    )
