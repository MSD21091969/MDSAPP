# Core Technologies & Dependencies

This project is built with Python and uses [Poetry](https://python-poetry.org/) for dependency management.

### Key Dependencies:
*   **Python 3.12+**
*   **`google-adk`**: The core framework for building intelligent agents and managing their lifecycle.
*   **`fastapi`**: The web framework for building the API endpoints.
*   **`uvicorn`**: An ASGI server for running the FastAPI application.
*   **`google-cloud-firestore`**: Client library for interacting with the Firestore NoSQL database.
*   **`google-generativeai`**: An underlying dependency used by the ADK for model interaction. Should not be used directly; all model interactions must go through `google-adk` abstractions like `LlmAgent`.
*   **`pydantic`**: Data validation and settings management using Python type hints.
*   **`celery`**: Distributed task queue for asynchronous background processing.
*   **`redis`**: An in-memory data structure store, used as a message broker and backend for Celery.
*   **`agentops`**: (Future Integration) For session replays, metrics, and monitoring of agent operations.
*   **`litellm`**: (Optional) For integrating with a wide range of LLMs beyond Gemini.
