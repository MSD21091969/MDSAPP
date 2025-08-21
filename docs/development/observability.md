# Observability

This document outlines the comprehensive observability strategy for the MDS, leveraging both built-in ADK features and custom integrations.

## Core Principles
*   **Visibility**: Gain deep insights into agent behavior, decision-making, and data flow.
*   **Traceability**: Track the lifecycle of a mission and its associated data from end-to-end.
*   **Performance Monitoring**: Identify bottlenecks and optimize agent execution.

## Observability Tools & Integrations

### 1. Standard Logging
*   **Current State**: Basic Python `logging` module is used for general application logs, directing messages to console/standard output.
*   **Future State (Phase 3)**: Integration with **Google Cloud Logging** for centralized, structured, and persistent logs. All application and Celery worker logs will be streamed here.

### 2. ADK Callbacks for Centralized Eventing

The Google Agent Development Kit (ADK) provides a powerful `Callbacks` mechanism that is central to our advanced observability strategy. Callbacks allow us to intercept events from the ADK runtime and route them to our centralized `CommunicationsManagement` service for comprehensive logging, tracing, and analysis.

#### How it Works:
1.  **Event Interception**: The ADK runtime emits various events during an agent's lifecycle (e.g., agent start/end, tool start/end, LLM request/response, artifact creation).
2.  **Custom Callback Handlers**: We implement custom Python classes (e.g., `CommManagerCallbackHandler`) that define methods for specific ADK events (e.g., `on_artifact_create`, `on_tool_end`, `on_llm_end`).
3.  **Centralized Routing**: Inside these callback methods, the event data is formatted and sent to the `CommunicationsManagement` service.
4.  **External Integration**: The `CommunicationsManagement` service acts as a central hub, which can then push this rich event data to external monitoring and logging platforms:
    *   **Google Cloud Logging**: For structured, searchable logs of all agent activities, including detailed event payloads.
    *   **Google Cloud Pub/Sub**: (Future Integration - Phase 3) For real-time event streaming, enabling downstream systems (e.g., analytics dashboards, alerting systems) to react to agent events as they happen.

### 3. Artifact Tracking for Data Lineage

The ADK's formal `Artifact` system provides automated data lineage. When tools consume or produce data (e.g., reading a CSV, writing a report), the ADK can automatically track these as artifacts. This creates a structured, auditable record of data flow through the entire workflow, crucial for debugging and understanding complex transformations.

### 4. Third-Party & Cloud Integrations
*   **AgentOps**: Provides session replays and detailed metrics for agent behavior. To enable it, initialize it in your main application entry point:
    ```python
    import agentops
    agentops.init()
    ```
*   **Google Cloud Trace**: For applications deployed to Google Cloud, tracing can be enabled to get a centralized dashboard of real traffic. This is enabled via the `--trace_to_cloud` flag during deployment with `adk deploy`.

### 5. Monitoring & Alerting
*   Key metrics (e.g., agent execution times, tool usage, LLM token usage) are collected via callbacks and integrated with monitoring platforms.
*   Alerting rules can be configured based on these metrics to notify teams of anomalies or performance degradation.