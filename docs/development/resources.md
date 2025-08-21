# Developer Resources & Examples

This document provides a collection of resources and examples for developers working on the MDS.

## General Resources

*   [Python Documentation](https://docs.python.org/3/)
*   [Poetry Documentation](https://python-poetry.org/docs/)
*   [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
*   [FastAPI Documentation](https://fastapi.tiangolo.com/)

## MDS Specific Examples

*   **Agent Implementation**: See `MDSAPP/agents/chat_agent.py` for an example of a tool-wielding agent.
*   **Tool Definition**: See `MDSAPP/core/tools/analysis_tools.py` for examples of how to define custom tools.
*   **Prompt Management**: See `MDSAPP/core/managers/prompt_manager.py` and `MDSAPP/CommunicationsManagement/prompts/` for how prompts are structured and managed.
*   **Casefile Usage**: See `MDSAPP/CasefileManagement/manager.py` for examples of interacting with Casefiles.

## Key Google Agent Development Kit (ADK) Concepts

The Google Agent Development Kit (ADK) provides several core concepts that are fundamental to building robust and intelligent agents. Understanding these concepts is crucial for effective development and expansion of the MDS.

### 1. State (`InvocationContext.session.state`)

*   **Purpose**: Manages short-term, in-memory data for a single, continuous execution flow or "session." It's a temporary scratchpad for passing information between agents within a single orchestrator run.
*   **Characteristics**: Ephemeral; data is lost once the top-level agent's `run` method completes.
*   **Usage in MDS**: Used by the `HQOrchestratorAgent` to pass the `casefile_id`, `mission`, and `workflow` objects to sub-agents during a single orchestration cycle.

### 2. Memory

*   **Purpose**: Provides long-term, persistent storage for agents, allowing them to remember information across multiple, independent sessions. This is for durable knowledge that an agent should retain over time (e.g., user preferences, learned patterns).
*   **Characteristics**: Persistent; data survives agent restarts and new sessions.
*   **Potential Usage in MDS**:
    *   `ChatAgent`: Could remember user preferences (e.g., preferred report formats, common data sources).
    *   `EngineerAgent`: Could store performance metrics or optimization strategies learned from past workflow executions to inform future engineering decisions.

### 3. Callbacks

*   **Purpose**: A powerful mechanism for observing and interacting with the agent's lifecycle. Callbacks are functions you register to be automatically invoked at specific points during an agent's execution (e.g., before/after a tool call, before/after an LLM interaction, when an artifact is created).
*   **Characteristics**: Event-driven; allows for non-intrusive integration of custom logic.
*   **Usage in MDS**: Crucial for advanced observability, logging, and tracing. By implementing custom callback handlers, the MDS can funnel all relevant events (tool executions, LLM interactions, artifact creation) into the `CommunicationsManagement` service for centralized analysis and external integration (e.g., Cloud Logging, Pub/Sub).

### 4. Artifacts

*   **Purpose**: A formal concept for tracking and managing data that is produced or consumed by agents and tools. An artifact represents a distinct piece of data (e.g., a file, a dataset, a report) that flows through the system.
*   **Characteristics**: Provides automated data lineage; captures inputs and outputs of tool calls.
*   **Usage in MDS**: When the `ExecutorAgent` runs a workflow, the ADK can automatically track files read (e.g., `/data/source.csv`) as input artifacts and files written (e.g., `/reports/summary.txt`) as output artifacts. Intermediate data (like analysis results) can also be formalized as artifacts, creating a complete, auditable chain of data transformations throughout the mission.