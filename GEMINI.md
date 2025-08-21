# MDS Documentation

This document provides a high-level overview and index for the MDS project documentation.

## Architecture

*   [Architectural Overview](./docs/architecture/overview.md)
*   [Architectural Components](./docs/architecture/components.md) (Detailed breakdown of agents and managers)
*   [Architectural Vision](./docs/architecture/vision.md)

## Project

*   [Project Overview](./docs/project/overview.md)
*   [Installation](./docs/project/installation.md)
*   [Running the Application](./docs/project/running.md)

## Development

*   [**Contributing Guidelines & Best Practices**](./CONTRIBUTING.md) (START HERE)
*   [Technology Stack & Versions](./docs/development/stack.md)
*   [Core Technologies & Dependencies](./docs/project/dependencies.md)
*   [Observability](./docs/development/observability.md)
*   [Developer Resources & Examples](./docs/development/resources.md)
*   [Recent Platform Updates](./docs/development/updates.md)

## Recent Platform Updates (September 2025)

### Google Agent Development Kit (ADK) Updates

*   **August 2025:** `gemini-1.5-flash/answer_gen/v1` model becomes the default in Vertex AI Search.
*   **IMPORTANT:** ALWAYS USE `gemini-2.5-flash` for all model interactions.
*   **July 2025:** Firebase Studio integration with "Agent mode," MCP support, and Gemini CLI integration.
*   **June 2025:** ADK v1.2.0 released, enabling direct deployment to the Vertex AI Agent Engine via a single CLI command.
*   **May 2025:** Python ADK reaches v1.0.0 (production-ready) and the initial Java ADK (v0.1.0) is launched.
*   **April 2025:** The ADK is officially introduced as an open-source framework at Google Cloud Next.
*   **Google I/O 2025 Announcements:** Further enhancements were announced at Google I/O 2025, including new versions of the ADK for Python and Java, an intuitive Agent Engine UI within the Google Cloud console for easier management, deployment, and monitoring, and continued improvements to the A2A protocol.
*   **Q3 2025 Roadmap:** Planned updates for the third quarter of 2025 include a configurable ADK, support for computer use tools, an ADK Github Assistant, and improvements to the ADK evaluation infrastructure and community repository.
*   **Future Outlook:** The next major announcements are expected at Google Cloud Next 2026 (April 22-24, 2026).

### Vertex AI Agent Engine & AI Applications

*   **General Availability:** The Vertex AI Agent Engine became generally available (GA) on March 4, 2025. It is a fully managed platform designed to streamline the deployment, management, and scaling of AI agents in production environments.
*   **Customization and Security:** As of August 7, 2025, users can utilize their own custom service accounts for agent identity, enabling more granular permission management.
*   **Framework Support:** The Vertex AI Agent Engine offers flexibility by supporting various agent frameworks, including LangChain, AutoGen 2, LlamaIndex, and CrewAI.
*   **New Features:** A "Memory Bank" feature for the Vertex AI Agent Engine became available in preview on July 3, 2025, allowing for the dynamic generation of long-term memories based on user conversations. Furthermore, a Data Science Agent (DSA) in Colab Enterprise was previewed on August 4, 2025, aimed at automating data analysis and model creation.
*   **Oracle Partnership:** Google's Gemini models are now available through the Oracle Cloud Infrastructure (OCI) Generative AI service, allowing for the creation of AI agents within the Oracle ecosystem.
*   **Agent Development:** The open-source Agent Development Kit (ADK) is available to facilitate the creation of complex, multi-agent systems.
*   **Expanded Generative Media:** Vertex AI now offers generative models for video (Veo 3), images (Imagen 4), and music (Lyria 2).
*   **Infrastructure Upgrades:** The 7th generation "Ironwood" TPUs and enhancements to the AI Hypercomputer provide more power for AI workloads.

### Model Context Protocol (MCP) Updates

*   **June 2025 (v2025-06-18):** This major update focused on production-readiness and included several key changes:
    *   **Security:** MCP servers are now classified as OAuth 2.0 Resource Servers, requiring clients to use "Resource Indicators" (RFC 8707) to bind tokens to specific servers.
    *   **Interactivity:** A new "Elicitation" feature allows servers to pause tool calls to request additional information from the user.
    *   **Tool Outputs:** The protocol now supports structured JSON for tool outputs.
    *   **Deprecation:** Support for JSON-RPC batching has been deprecated.
*   **March 2025 (v2025-03-26):** This earlier update introduced a comprehensive OAuth 2.1 authorization framework, a more flexible streamable HTTP transport, and added support for audio data, alongside existing text and image content types.
*   **Adoption:**
    *   **June 2025:** Native MCP integration was introduced in LM Studio and VSCode.
    *   **May 2025:** Microsoft added native MCP support to Copilot Studio.
    *   **April 2025:** Google DeepMind confirmed that upcoming Gemini models will support MCP.

### AgentOps Updates

*   **Platform Focus:** The platform continues to enhance the developer experience with a focus on observability, "Time Travel Debugging," cost management, and expanded integrations.
*   **Integrations:** AgentOps has expanded its integrations, now seamlessly supporting Google's ADK for end-to-end tracking and debugging. It also integrates natively with Agno and Microsoft's Agent Lightning, in addition to existing integrations with frameworks like CrewAI, Langchain, and AutoGen.
*   **New Capabilities:** An autonomous agent has been deployed at AgentOps to generate weekly product update threads directly from GitHub PRs. The platform offers comprehensive observability, real-time monitoring, cost control, failure detection, and detailed tool usage statistics.
*   **Industry Growth:** The AgentOps field is rapidly expanding, with new tools and platforms emerging to manage complex AI systems. IBM has launched an AgentOps solution, and other platforms like Agenta are actively developing new features.
*   **Standardization:** Google's Agent2Agent (A2A) protocol for inter-agent communication is now under the stewardship of the Linux Foundation, a key step towards industry-wide standards.

## Project Status and Next Steps (As of August 20, 2025)

The project has successfully moved from an initial architectural phase to a functional, proof-of-concept prototype. The following sections detail our recent accomplishments, the current state of the system, and the strategic plan for evolving the application into a robust, scalable, and secure platform.

### Recent Accomplishments (Mid-August 2025)

A focused debugging session resolved several critical, foundational bugs, moving the application from a non-functional to a working state:

*   **Web Interface Implemented**: A functional web-based chat interface has been successfully developed and integrated, allowing users to interact with the `ChatAgent` for casefile management and engineering tasks. This involved setting up static file serving, configuring CORS, and aligning frontend-backend communication protocols.
*   **Application Startup Reliability:** Resolved a `NameError` on startup by correcting a missing import, allowing the application to run reliably.
*   **Asynchronous Operations:** Fixed a core `AttributeError` related to an un-awaited coroutine (`load_casefile`). This unblocked the entire agent orchestration flow, enabling agents to correctly retrieve and process data.
*   **Data Integrity:** Corrected a major bug in the `CasefileManager` where sub-casefiles were not being saved independently to the database. This fix ensures the integrity of the hierarchical casefile structure and allows workflows that create sub-casefiles to complete successfully.
*   **Enhanced Prompt Engineering & Workflow Reliability:** Significant improvements have been made to the system's prompt engineering and workflow generation capabilities:
    *   **Robust Workflow Generation:** Addressed Pydantic validation errors in `Workflow` models, ensuring the `ProcessorAgent` can reliably generate and self-correct workflow definitions. This involved refining the `WorkflowCondition` model and enhancing the `llm_parser` to provide detailed error feedback to the LLM during self-correction.
    *   **Casefile Management Integration:** The `ChatAgent` now leverages `CasefileManager` tools for comprehensive casefile management.
    *   **Dataset Production Orchestration:** The `EngineerAgent` has been extended with a `produce_dataset` tool, enabling the `ChatAgent` to instruct the "workflow engineer" to initiate dataset production for casefiles. The `ChatAgent`'s prompt has been updated to guide its LLM in utilizing this new capability. These enhancements significantly improve the system's ability to manage and process information related to casefiles.

### Current System Status

This is an honest assessment of the system against our key design goals:

| Goal | Status & Assessment |
| :--- | :--- |
| **Robustness** | **Improved, but more work is needed.** The major crashing bugs have been fixed. The system now has a functional web interface, improving user interaction. However, it still lacks comprehensive error handling and retry mechanisms for operations like API calls or data processing. **Workflow generation is significantly more robust due to prompt engineering improvements.** |
| **Reliability** | **Significantly Improved.** The application now reliably starts and can complete its core workflows, making its behavior predictable. The web interface provides a stable way for users to interact with the system. |
| **Scalability** | **Limited (Prototype-Level).** The current architecture is a single-instance prototype. Key limitations include data duplication in the database, reliance on in-process caching (`lru_cache`), and synchronous, in-process task execution that is not suitable for long-running jobs. |
| **Safety** | **Minimal.** The system currently lacks foundational security features. There are no user authentication, role-based permissions, or robust write-guarding mechanisms to prevent race conditions. |

### Next Steps: The Path to a Scalable System

The following three-phase strategy will systematically evolve the prototype into a production-ready application.

---

#### Phase 1: Decouple Task Execution (Highest Priority)

**Goal:** Move long-running agent processes out of the synchronous API request cycle to make the API fast and reliable.

1.  **Integrate a Task Queue:** Add **Celery** and **Redis** to the project. The `WorkflowManager` will be activated to place jobs on the queue instead of calling agents directly.
2.  **Create Background Workers:** Move the `HQOrchestrator`'s logic into a Celery task, allowing the entire agent orchestration to happen asynchronously in a separate worker process.
3.  **Implement Asynchronous Feedback:** The API will immediately return a `task_id`. New endpoints will be created to allow clients to poll for task status, which will be updated by the background workers.

---

#### Phase 2: Scale the Database and State Management

**Goal:** Address data duplication and prepare the database for higher throughput and concurrent access.

1.  **Refactor Data Models:** Modify the `Casefile` model to store a list of sub-casefile IDs instead of embedding the full objects, eliminating data duplication.
2.  **Implement Transactions:** Wrap complex, multi-step database operations (like casefile creation) in a single transaction to ensure data consistency and prevent partially-completed states.
3.  **Centralize Caching:** If required, replace in-process caching with a shared **Redis** cache to ensure consistency across all API and worker processes.

---

#### Phase 3: Harden with Security and Production Best Practices

**Goal:** Secure the application and make it fully production-ready, manageable, and observable.

1.  **Implement Auth & RBAC:** Integrate **OAuth2** for user authentication and create a role-based access control (RBAC) system to manage permissions for all operations.
2.  **Introduce Human-in-the-Loop Controls:** Add an "approval" step to the workflow lifecycle. The system will generate plans but wait for user approval via a dedicated API endpoint before dispatching them for execution.
3.  **Integrate with Cloud Operations Suite:**
    *   **Google Cloud Logging:** Pipe all logs from the FastAPI app and Celery workers into a centralized, structured logging system.
    *   **Google Cloud Pub/Sub:** Use Pub/Sub to publish real-time status updates from workers, allowing for an event-driven architecture and responsive frontend experiences.
4.  **Advanced Workflow & Agent Capabilities:**
    *   **Workflow Management (Process & Execution):** Further enhance the system's ability to manage and execute complex workflows, including advanced process orchestration and monitoring.
    *   **Workflow Engineering (Data Research):** Develop capabilities for the "workflow engineer" (e.g., `EngineerAgent`) to perform sophisticated data research, analysis, and generation for casefiles, moving beyond basic dataset production.
    *   **ChatAgent as RAG Data Object Manager:** Evolve the `ChatAgent` to act as a comprehensive manager for Retrieval Augmented Generation (RAG) data objects, enabling it to intelligently retrieve, synthesize, and present information from various data sources to the user. This will include managing the lifecycle of RAG data and optimizing its use in conversational interactions.

---

#### Phase 4: Enhanced User Interface & Experience

**Goal:** Evolve the basic web chat interface into a comprehensive, user-friendly, and visually appealing application for managing casefiles and interacting with agents.

1.  **Dynamic Casefile Selection:** Implement UI elements that allow users to easily select and switch between existing casefiles, rather than relying on a hardcoded default ID.
2.  **Casefile Creation from UI:** Provide a user-friendly interface for creating new casefiles directly from the web application, including input fields for name, description, and optional parent ID.
3.  **Improved Chat History Display:** Enhance the visual presentation of chat history, including distinct styling for user and agent messages, timestamps, and better rendering of structured outputs (e.g., tool calls, JSON responses).
4.  **Real-time Updates & Notifications:** Leverage the existing Pub/Sub integration to provide real-time updates on agent progress, workflow execution status, and other relevant system events directly within the UI.
5.  **User-Friendly Error Handling & Feedback:** Implement more informative and actionable error messages, along with visual cues and notifications to guide the user through potential issues.
6.  **Basic Casefile Management UI:** Develop dedicated sections or components for listing all casefiles, viewing their details (e.g., event logs, associated workflows, research results), and performing basic management operations (e.g., edit description, delete).
7.  **Responsive Design & Accessibility:** Ensure the entire web interface is fully responsive, adapting seamlessly to various screen sizes (desktop, tablet, mobile), and adheres to accessibility best practices.
8.  **Visual Polish & User Experience (UX):** Refine the overall aesthetic, implement intuitive navigation, and optimize user flows to provide a smooth, efficient, and enjoyable user experience.
