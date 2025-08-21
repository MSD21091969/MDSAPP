
import pytest
import asyncio
import json # Added import
from unittest.mock import MagicMock, AsyncMock

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.CasefileManagement.models.casefile import Casefile
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.agents.hq_orchestrator import HQOrchestratorAgent
from MDSAPP.agents.processor_agent import ProcessorAgent
from MDSAPP.agents.executor_agent import ExecutorAgent
from MDSAPP.agents.engineer_agent import EngineerAgent

# Mock the GenerativeModel to return predictable JSON
mock_model = MagicMock()
mock_model.generate_content_async = AsyncMock()

from MDSAPP.core.managers.database_manager import DatabaseManager

@pytest.fixture
def casefile_manager():
    """Fixture for a fresh CasefileManager with a mocked in-memory database."""
    mock_db_manager = MagicMock(spec=DatabaseManager)
    
    # Simulate an in-memory store for casefiles
    _casefiles_store = {}

    def mock_save_casefile(casefile: Casefile):
        _casefiles_store[casefile.id] = casefile
        
    def mock_load_casefile(casefile_id: str) -> Casefile | None:
        return _casefiles_store.get(casefile_id)

    def mock_load_all_casefiles() -> list[Casefile]:
        return list(_casefiles_store.values())

    def mock_delete_casefile(casefile_id: str) -> bool:
        if casefile_id in _casefiles_store:
            del _casefiles_store[casefile_id]
            return True
        return False

    mock_db_manager.save_casefile.side_effect = mock_save_casefile
    mock_db_manager.load_casefile.side_effect = mock_load_casefile
    mock_db_manager.load_all_casefiles.side_effect = mock_load_all_casefiles
    mock_db_manager.delete_casefile.side_effect = mock_delete_casefile

    manager = CasefileManager(db_manager=mock_db_manager)
    
    # Directly create Casefile and save it via the mocked db_manager
    casefile = Casefile(name="Test Casefile", description="Test description for HQ flow", mission="Test mission for the HQ flow")
    mock_db_manager.save_casefile(casefile)
    return manager, casefile.id

from google.generativeai.types import FunctionDeclaration

@pytest.fixture
def tool_registry():
    """Fixture for a mocked ToolRegistry."""
    registry = MagicMock(spec=ToolRegistry)

    # Mock the get_all_tool_declarations method
    def mock_get_all_tool_declarations():
        return [
            {
                "name": "mock_tool",
                "description": "A mock tool for testing purposes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"],
                },
            }
        ]
    registry.get_all_tool_declarations.side_effect = mock_get_all_tool_declarations

    # Register the mock tool handler
    def mock_tool_handler(message: str):
        return {"status": "ok", "input": message}
    registry.get_tool_handler.return_value = mock_tool_handler

    return registry

from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import Session, InMemorySessionService
import uuid

@pytest.mark.asyncio
async def test_full_hq_flow(casefile_manager, tool_registry):
    """
    Tests the full orchestration flow from Mission -> Plan -> Execute -> Analyze.
    """
    manager, casefile_id = casefile_manager

    # 1. Setup - Instantiate all agents
    processor_agent = ProcessorAgent(name="TestProcessor", model=mock_model, prompt_manager=MagicMock(), retriever=MagicMock(), tool_registry=tool_registry)
    executor_agent = ExecutorAgent(name="TestExecutor", tool_registry=tool_registry)
    engineer_agent = EngineerAgent(name="TestEngineer", model=mock_model, prompt_manager=MagicMock(), casefile_manager=manager, tool_registry=tool_registry)

    # The HQ Orchestrator ties everything together
    hq_orchestrator = HQOrchestratorAgent(
        name="TestHQ",
        casefile_manager=manager,
        tool_registry=tool_registry,
        processor_agent=processor_agent,
        executor_agent=executor_agent,
        engineer_agent=engineer_agent
    )

    # Mock the LLM responses for Processor and Engineer
    # Mock Processor to return a simple workflow
    mock_processor_response = {
        "workflow_id": "wf-test-123",
        "type": "analysis", # Changed from "TESTING"
        "elements": [{
            "id": "el-test-1", "name": "Run Mock Tool", "type": "tool", # Changed from "TOOL"
            "instruction": "Run the mock tool with a test message.",
            "metadata": {"tool_name": "mock_tool", "arguments": {"message": "hello"}}
        }],
        "dynamics": {"nodes": [{"element_id": "el-test-1"}], "edges": [], "execution_mode": "sequential", "start_node_id": "el-test-1"} # Changed from "SEQUENTIAL"
    }
    # Mock Engineer to return a simple engineered workflow
    mock_engineer_response = {
        "engineered_workflow_id": "eng-wf-test-456",
        "name": "Engineered Test Workflow",
        "description": "An optimized workflow for testing.",
        "tags": ["engineered", "test"],
        "elements": [],
        "dynamics": {"nodes": [], "edges": [], "execution_mode": "sequential", "start_node_id": ""} # Changed from "SEQUENTIAL"
    }

    # Helper to create a mock InvocationContext
    def create_mock_context(current_casefile_id: str, initial_state: dict = None):
        session_service = InMemorySessionService()
        mock_session = Session(
            id=f"mock_session_for_{current_casefile_id}",
            app_name="MDSAPP_Test",
            user_id="test_user",
            state=initial_state or {"casefile_id": current_casefile_id}
        )
        return InvocationContext(
            session=mock_session,
            session_service=session_service,
            invocation_id=str(uuid.uuid4()),
            agent=hq_orchestrator
        )

    # --- STAGE 1: Mission to Plan ---
    print("\n--- Testing Stage 1: Processor ---" )
    mock_model.generate_content_async.return_value.text = json.dumps(mock_processor_response)
    
    ctx_stage1 = create_mock_context(casefile_id)
    async for event in hq_orchestrator._run_async_impl(ctx_stage1):
        if event.is_final_response():
            print(f"HQ Final Response (Processor): {event.content.parts[0].text}")

    casefile = manager.load_casefile(casefile_id)
    assert len(casefile.workflows) == 1
    assert casefile.workflows[0].workflow_id == "wf-test-123"
    assert not casefile.execution_results
    print("Processor test PASSED.")

    # --- STAGE 2: Plan to Execution ---
    print("\n--- Testing Stage 2: Executor ---" )
    # Executor does not use LLM, so no mock_model.generate_content_async needed here
    ctx_stage2 = create_mock_context(casefile_id)
    async for event in hq_orchestrator._run_async_impl(ctx_stage2):
        if event.is_final_response():
            print(f"HQ Final Response (Executor): {event.content.parts[0].text}")

    casefile = manager.load_casefile(casefile_id)
    assert len(casefile.execution_results) == 1
    assert casefile.execution_results[0].workflow_id == "wf-test-123"
    assert casefile.execution_results[0].steps[0].status.value == "completed"
    assert not casefile.engineered_workflows
    print("Executor test PASSED.")

    # --- STAGE 3: Execution to Analysis ---
    print("\n--- Testing Stage 3: Engineer ---" )
    mock_model.generate_content_async.return_value.text = json.dumps(mock_engineer_response)

    ctx_stage3 = create_mock_context(casefile_id)
    async for event in hq_orchestrator._run_async_impl(ctx_stage3):
        if event.is_final_response():
            print(f"HQ Final Response (Engineer): {event.content.parts[0].text}")

    casefile = manager.load_casefile(casefile_id)
    assert len(casefile.engineered_workflows) == 1
    assert casefile.engineered_workflows[0].engineered_workflow_id == "eng-wf-test-456"
    print("Engineer test PASSED.")

