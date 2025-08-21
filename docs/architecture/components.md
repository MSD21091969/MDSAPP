# Architectural Components

This document provides a detailed overview of the core components within the `MDSAPP`. The architecture separates **Agents** (the actors) from **Management Modules** (the services they use).

## 1. The Agents (`MDSAPP/agents/`)

The agents are the primary actors in the system, each with a specialized role in the **Define, Translate, Execute** pipeline.

*   **`hq_orchestrator.py`**: The master orchestrator. It drives the overall **Define, Translate, Execute** pipeline by inspecting the `Casefile`'s state and delegating tasks to specialist agents. Its execution is now handled asynchronously by a Celery worker, ensuring responsiveness of the main API.

*   **`chat_agent.py`**: The primary user interface. It handles conversational interactions, interprets user requests, and can initiate new missions or query the status of existing ones. It relies heavily on the `CommunicationManager` for managing conversational context and the `PromptManager` for its persona.

*   **`processor_agent.py` (Definer)**: Responsible for **defining** standard workflows. It takes a high-level mission (from the `Casefile`) and, using an LLM, generates a detailed, platform-agnostic `Workflow` object. This object is an abstract blueprint for how to achieve the mission, which is then saved back to the `Casefile`.

*   **`engineer_agent.py` (Definer/Optimizer)**: Responsible for **analysis and optimization**. It reviews completed workflow executions and their `WorkflowExecutionResult` (from the `Casefile`) and designs an optimized, reusable `EngineeredWorkflow` object. Like the `ProcessorAgent`, it produces a platform-agnostic blueprint, but one that is refined through analysis. It also produces `ResearchResult` objects to summarize its findings, which are saved to the `Casefile`.

*   **`executor_agent.py` (Translator/Initiator)**: This is a role for a **platform-specific specialist**. The `ADK_Executor`, for example, is responsible for two key steps:
    1.  **Translating:** It takes a platform-agnostic `Workflow` or `EngineeredWorkflow` object and translates its `WorkflowDynamics` graph into a concrete, executable agent flow for the Google ADK.
    2.  **Initiating:** It hands off the translated flow to the ADK's runtime engine for execution. It then captures the outcome as a `WorkflowExecutionResult`, which is saved back to the `Casefile`.
    Other executors could be developed for different platforms (e.g., `LangChain_Executor`).

*   **`api.py`**: The FastAPI router for agent-related actions. It now primarily serves as an entry point to dispatch asynchronous tasks to the `WorkflowManager` (which then uses Celery) for long-running operations like triggering the `HQOrchestrator`.

## 2. The Management Modules (Services)

These modules provide the business logic and data handling services that the agents use to perform their tasks.

### `CasefileManagement`
This module is responsible for the entire lifecycle of casefiles, acting as the central data store for all mission-related artifacts.
*   **`manager.py`**: The `CasefileManager` class contains the core business logic for CRUD operations on casefiles, including handling their hierarchical structure (parent/sub-casefiles). Recent improvements ensure robust persistence of sub-casefiles.
*   **`models/casefile.py`**: Defines the Pydantic model for the `Casefile`. This central object contains everything related to a mission, including STIX-inspired objects like `Campaign` (for the mission definition) and `Grouping` (for the data dossier), as well as `Workflow` objects, `WorkflowExecutionResult`, and `ResearchResult`.
*   **`api/v1.py`**: The FastAPI router for casefile-related API endpoints.

### `CommunicationsManagement`
This module handles all user-facing communication, primarily through the `ChatAgent`, and manages conversational context and agent prompts.
*   **`manager.py`**: The `CommunicationManager` orchestrates the interaction between the user, the API, and the `ChatAgent`, and manages conversational context.
*   **`prompts/CHAT.json`**: The core prompt that defines the persona and behavior of the `ChatAgent`.

### `WorkFlowManagement`
This module is responsible for defining and storing the abstract `Workflow` blueprints, and for dispatching workflow-related tasks to background workers.
*   **`manager.py`**: The `WorkflowManager` dispatches workflow-related tasks (like orchestration) to background Celery workers.
*   **`models/workflow.py`**: Defines the core, platform-agnostic data structures for workflows, including `Element`, `WorkflowDynamics`, `Workflow`, and `EngineeredWorkflow`.
*   **`models/results.py`**: Defines data models for workflow execution results.
*   **`workers/workflow_tasks.py`**: Contains the Celery tasks that execute the actual workflow logic in the background.

### `Core`
This directory contains the core, cross-cutting concerns of the application, such as dependency injection, external API services, and shared utilities and data models.
*   **`managers/database_manager.py`**: Manages the connection to the Firestore database and handles all CRUD operations for casefiles and other data.
*   **`managers/tool_registry.py`**: Manages the registration and lookup of tools that agents can use.
*   **`managers/prompt_manager.py`**: Manages the loading and retrieval of prompts for various agents.
*   **`services/`**: Contains various service modules for interacting with external APIs (e.g., Google Workspace).
*   **`utils/`**: Contains shared utility functions and helper classes.