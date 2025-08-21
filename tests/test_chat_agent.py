import pytest
from unittest.mock import AsyncMock, MagicMock
from MDSAPP.agents.chat_agent import ChatAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

def test_chat_agent_initialization():
    # Mock dependencies
    mock_model = AsyncMock()
    mock_prompt_manager = AsyncMock()
    mock_retriever = AsyncMock()
    mock_casefile_manager = AsyncMock()
    mock_drive_manager = AsyncMock()
    mock_tool_registry = MagicMock()
    mock_tool_registry._tool_handlers = {}
    mock_tool_registry.get_all_tool_declarations.return_value = []

    # Initialize the ChatAgent
    chat_agent = ChatAgent(
        name="TestChatAgent",
        model=mock_model,
        prompt_manager=mock_prompt_manager,
        retriever=mock_retriever,
        casefile_manager=mock_casefile_manager,
        drive_manager=mock_drive_manager,
        tool_registry=mock_tool_registry
    )

    # Assert that the agent is initialized correctly
    assert chat_agent.name == "TestChatAgent"

@pytest.mark.asyncio
async def test_chat_agent_run_async_impl():
    # Mock dependencies
    mock_model = AsyncMock()
    mock_prompt_manager = AsyncMock()
    mock_retriever = AsyncMock()
    mock_casefile_manager = AsyncMock()
    mock_drive_manager = AsyncMock()
    mock_tool_registry = MagicMock()
    mock_tool_registry._tool_handlers = {}
    mock_tool_registry.get_all_tool_declarations.return_value = []

    # Configure the mock model to return a mock response
    mock_model.generate_content_async.return_value.text = "Hello from the mock model"

    # Initialize the ChatAgent
    chat_agent = ChatAgent(
        name="TestChatAgent",
        model=mock_model,
        prompt_manager=mock_prompt_manager,
        retriever=mock_retriever,
        casefile_manager=mock_casefile_manager,
        drive_manager=mock_drive_manager,
        tool_registry=mock_tool_registry
    )

    # Create a mock parent agent
    mock_parent_agent = BaseAgent(name="ParentAgent")

    # Create a mock InvocationContext
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", state={"user_input": "Hello"})
    mock_parent_context = InvocationContext(
        session_service=session_service,
        session=session,
        invocation_id="test_invocation",
        agent=mock_parent_agent,
    )

    # Call the run_async method
    events = [event async for event in chat_agent.run_async(mock_parent_context)]

    # Assert that the agent returns a response
    assert len(events) > 0
