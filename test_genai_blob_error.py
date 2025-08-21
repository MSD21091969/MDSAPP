# test_adk_chat_agent_integration.py

import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.types import Content, Part

# Import the dependency injection getter for the agent
from MDSAPP.core.dependencies import get_high_level_chat_agent, initialize_managers, register_all_tools, get_tool_registry

@pytest.mark.asyncio
async def test_chat_agent_responds_without_error():
    """
    Integration test to verify that the refactored ChatAgent can be initialized
    and responds to a simple message through the ADK Runner without errors.
    This validates that the model loading and core wiring is correct.
    """
    # 1. Initialize all managers and tools, just like in main.py
    # This is necessary because the agent depends on them.
    initialize_managers()
    tool_registry = get_tool_registry()
    register_all_tools(tool_registry)

    # 2. Get the agent instance from our dependency system
    chat_agent = get_high_level_chat_agent()
    assert chat_agent is not None, "Failed to get ChatAgent from dependencies"

    # 3. Set up the ADK Runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=chat_agent,
        session_service=session_service,
        app_name="test_app"
    )

    # 4. Create a session and send a message
    user_id = "test_user"
    session_id = "test_session"
    await session_service.create_session(app_name="test_app", user_id=user_id, session_id=session_id)

    message = Content(role="user", parts=[Part(text="Hello, are you working?")])

    # 5. Run the agent and check for a response
    final_response = None
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print(f"Agent Response: {final_response}")
    except Exception as e:
        pytest.fail(f"Agent run failed with an unexpected exception: {e}")

    # 6. Assert that we received a response
    assert final_response is not None, "Agent did not produce a final response."
    assert isinstance(final_response, str), f"Expected a string response, but got {type(final_response)}"
    assert len(final_response) > 0, "Agent returned an empty response."