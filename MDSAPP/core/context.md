# Core Module Context

This module serves as the foundational layer of the MDS, containing core, cross-cutting concerns and shared components that are utilized across all agents and management modules. It provides essential services, utilities, and data models that enable the overall system functionality.

## CONTEXT: Runtime & Managers
*   **`dependencies.py`**: Manages dependency injection, ensuring that singleton instances of key components (like managers and services) are consistently provided throughout the application.
*   **`managers/`**: Houses critical managers that provide application-wide services, including:
    *   `ToolRegistry`: Centralized registry for all available tools, enabling agents to discover and invoke functionalities.
    *   `PromptManager`: Manages access to prompt templates, crucial for LLM interactions across various agents.
    *   `DatabaseManager`, `EmbeddingsManager`, `EventManager`: Provide foundational data and event handling capabilities.

## CONTEXT: Shared Components & Utilities
*   **`models/`**: Defines core data models (e.g., `Dossier`, `Ontology`, `PromptStructure`) that are shared and understood across different parts of the system.
*   **`services/`**: Contains services that interact with external APIs (e.g., Google Drive, Firestore) or provide specialized functionalities (e.g., data retrieval, Google Workspace integration).
*   **`utils/`: Provides common utility functions (e.g., `data_generator`, `document_parser`, `llm_parser`) that support various operational needs of the agents and managers.

## Development Status / Roadmap

### Current Status:
*   Core managers (`ToolRegistry`, `PromptManager`, `DatabaseManager`, `EmbeddingsManager`, `EventManager`) are functional and provide stable foundational services.
*   Shared components and utilities are robust and support the overall application architecture, including the HQ orchestration flow.

### Next Steps / Focus Areas:
*   **Continued Support for HQ Flow:** Ensure core components seamlessly support the evolving requirements of the HQ orchestration flow and other agentic behaviors.
*   **Tool and Service Expansion:** Continue adding and integrating new tools and enhancing existing services to expand overall application capabilities.
*   **Performance and Scalability:** Continuously evaluate and implement strategies for optimizing performance and scaling core services to meet growing demands.
*   **Robustness and Observability:** Further enhance error handling, logging, and monitoring within core components to ensure system stability and provide deep insights.


