# Casefile Management Module Context

This module is central to the MDS, responsible for the entire lifecycle and persistence of `Casefile` objects. The `Casefile` acts as the single source of truth and the primary stateful object for any given mission, tracking its progress through planning, execution, and analysis.

## CONTEXT: Core Logic & Models
*   **`manager.py`**: The `CasefileManager` class contains the core business logic for creating, retrieving, updating, and deleting `Casefile` instances. It exposes its methods as tools, allowing AI agents (especially the `HQOrchestratorAgent`) to interact with and modify the mission's state.
*   **`models/casefile.py`**: Defines the Pydantic model for the `Casefile` object itself, including fields for the mission brief, generated workflows, execution results, and engineered workflows.

## CONTEXT: API Endpoints
*   **`api/v1.py`**: The FastAPI router for casefile-related API endpoints, allowing external systems or user interfaces to interact with casefiles.

## Development Status / Roadmap

### Current Status:
*   Core CRUD operations for `Casefile` objects are functional, including the ability to create and update `Casefile` instances with structured `Mission` objects.
*   `Casefile` serves as the central state for the `HQOrchestrator` flow.

### Next Steps / Focus Areas:
*   **Refine and Expand RBAC**: Enhance the current RBAC model with more granular permissions and explore more complex user/group management strategies.
*   **Data Storage**: Evaluate and potentially integrate more robust, scalable storage solutions (e.g., Firestore, dedicated database) for `Casefile` persistence.
*   **Versioning**: Implement versioning for `Casefile` changes to track historical states and enable rollbacks.
*   **Complex Data Structures**: Enhance `Casefile` to accommodate more complex data structures, especially for handling multiple datasets and analysis results as per `ChatAgent`'s future needs.
*   **Search & Query**: Develop capabilities to search and query `Casefile` contents efficiently.


