# Architectural Vision

The project is designed to evolve into a dynamic and intelligent multi-agent system, leveraging advanced ADK features and open standards:

*   **Multi-Agent Collaboration (A2A):** Agent-to-Agent communication will be based on the open A2A protocol. In mid-2025, this protocol was donated to the Linux Foundation, ensuring open, community-driven development and broad industry adoption (including from Amazon and Microsoft). This strengthens our ability to build interoperable agents that can be discovered and consumed via platforms like the upcoming AI Agent Marketplace. 
*   **Standardized Tool Integration (MCP):** Tools will be exposed and consumed using the **Model Context Protocol (MCP)**, allowing for interoperability with a broader ecosystem of applications and services.
*   **Advanced Control and Observability**: We will leverage ADK **Callbacks** and **Plugins** to implement fine-grained control, monitoring, and features like user approval gates and real-time intervention points.
*   **Grounding**: Agents will be grounded using **Google Search** for real-time public information and **Vertex AI Search** for querying private, enterprise knowledge bases, ensuring responses are accurate and verifiable.

## Path to a Scalable System

To evolve the current functional prototype into a production-ready application, the following strategic phases will be implemented:

### Phase 1: Decouple Task Execution

The highest priority is to move long-running agent processes out of the synchronous API request cycle. This will be achieved by integrating a **Celery** task queue with a **Redis** message broker. This makes the user-facing API fast and reliable, with all heavy processing handled by asynchronous background workers.

### Phase 2: Scale the Database and State Management

This phase focuses on preparing the database for higher throughput and concurrent access. Key actions include refactoring the data models to eliminate data duplication (storing sub-casefile IDs instead of full objects) and wrapping complex database operations in transactions to ensure data consistency.

### Phase 3: Harden with Security and Production Best Practices

The final phase will make the application secure, manageable, and observable. This includes implementing **OAuth2** for authentication, Role-Based Access Control (RBAC) for permissions, and integrating with **Google Cloud Logging** and **Google Cloud Pub/Sub** for centralized observability and real-time, event-driven notifications.
