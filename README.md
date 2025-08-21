# MDS7 - Modular Data System

This repository contains the codebase for MDS7, a modular data system designed for advanced data analysis and processing using AI agents.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Testing the API](#testing-the-api)
- [Architecture Overview](#architecture-overview)

## Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.12+**: The application is developed with Python 3.12.
- **Poetry**: Used for dependency management. Install it via `pip install poetry` or refer to the [official Poetry documentation](https://python-poetry.org/docs/#installation).
- **Google Cloud SDK**: Used for authenticating with Google Cloud. Install it by following the [official documentation](https://cloud.google.com/sdk/docs/install).

## Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd mds7
    ```
2.  **Install project dependencies using Poetry:**
    ```bash
    poetry install
    ```

## Environment Setup
The application is configured to use Google Cloud Vertex AI. You must authenticate using Application Default Credentials (ADC).

**1. Authenticate with the Google Cloud CLI:**
```bash
gcloud auth application-default login
```

**2. Set the quota project:**
```bash
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```
Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

**3. Configure the `.env` file:**
Ensure your `.env` file in the project root contains the following variables, as the application relies on them to connect to the correct Vertex AI project:
```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION"
```


## Running the Application
```bash
poetry run uvicorn MDSAPP.main:app --reload
```
The API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

## Testing the API
Once the FastAPI server is running:

1.  **Access Swagger UI:** Open your web browser and navigate to `http://127.0.0.1:8000/docs`.
2.  **Test Endpoints:**
    *   **Casefile Management:** Use the endpoints under "Casefile Management" to create, retrieve, and delete casefiles.
    *   **Chat:** Use the endpoint under "Chat" to interact with the `ChatAgent`.
    *   **HQ Orchestrator:** Use the endpoint under "HQ Orchestrator" to trigger the `hqflow`.

## Current Status (August 20, 2025)

The project is currently a **functional proof-of-concept prototype**. Recent development has focused on fixing critical bugs to ensure core workflows are operational. The application can now successfully run its primary planning and execution flows.

However, the system is not yet production-ready. The immediate next steps involve a strategic plan to improve scalability, robustness, and security by integrating a background task queue (Celery), refactoring the database schema, and implementing security features.

For a detailed breakdown of recent accomplishments, the current system status, and the full strategic plan for scaling the application, please see the main project documentation hub:

*   **[Project Status and Next Steps](./GEMINI.md)**

## Architecture Overview
MDS7 employs a modular, agent-based architecture:
-   **FastAPI Server:** Handles API requests and dispatches background tasks.
-   **Specialized LLM Agents:**
    -   **Chat Agent:** Direct user interaction, conversational interface.
    -   **Workflow Processor Agent:** Plans and decomposes high-level missions into structured workflows.
    -   **Workflow Executor Agent:** Simulates the execution of workflows and reports on their outcomes.
    -   **Workflow Engineer Agent:** Analyzes executed workflows to create reusable templates.
    -   **HQ Orchestrator Agent:** The master agent that orchestrates the other agents.
-   **Firestore:** Used as the primary database for storing casefiles and their associated data (workflows, execution results, engineered workflows).
-   **Google ADK & Vertex AI:** Used for building and running the LLM-driven agents.

For a more detailed architectural overview, please refer to the documentation in the `docs/` directory.

