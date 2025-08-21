# Technology Stack & Versions

This project relies on the following core components. The versions listed reflect the latest updates as of August 20, 2025.

*   **Python**
    *   **Project Version**: `~3.12` (compatible with `>=3.12,<3.13`)
    *   **Version Status**: Python 3.12 is in the security-only support phase as of Q4 2024. For active development with bug fixes, an upgrade to Python 3.13+ should be considered.
    *   **ADK Supported**: `3.10+` / `3.12+`
    *   **Vertex AI Agent Engine Supported**: `3.9` - `3.13`

*   **Google Agent Development Kit (ADK)**
    *   **Package**: `google-adk`
    *   **Version**: `1.11.0` (Released: 2025-08-14)

*   **Web Framework**
    *   **Framework**: FastAPI
    *   **Package**: `fastapi`
    *   **Version**: `^0.111.0`
    *   **ASGI Server**: Uvicorn
    *   **Package**: `uvicorn`
    *   **Version**: `^0.30.1`

*   **Database**
    *   **Type**: NoSQL Document Database
    *   **Service**: Google Cloud Firestore
    *   **Package**: `google-cloud-firestore`
    *   **Version**: `^2.17.0`

*   **AI/LLM**
    *   **Service**: Google Gemini Models (via Google Generative AI API)
    *   **Package**: `google-generativeai`
    *   **Version**: `^0.7.1`
    *   **Package**: `google-ai-generativelanguage`
    *   **Version**: `^0.6.4`
    *   **Package**: `google-cloud-aiplatform`
    *   **Version**: `^1.56.0`

*   **Data Validation**
    *   **Package**: `pydantic`
    *   **Version**: `^2.7.4`

*   **Asynchronous Task Queue**
    *   **System**: Celery
    *   **Package**: `celery`
    *   **Version**: `^5.4.0`
    *   **Message Broker/Backend**: Redis
    *   **Package**: `redis`
    *   **Version**: `^5.0.5`
