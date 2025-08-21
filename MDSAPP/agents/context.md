# Agents Module Context

This module contains all the AI agents, which are the primary actors in the MDS. They are designed to be specialized, LLM-driven, and interact within orchestrated flows, leveraging Google ADK capabilities.

## CONTEXT: Orchestration
*   **`hq_orchestrator.py`**: The master orchestrator. Implemented as a `BaseAgent`, it manages the full `Mission -> Plan -> Execute -> Analyze` lifecycle for a given `Casefile`. It inspects the `Casefile` state and delegates tasks to specialist agents using `AgentTool`s.
*   **`api.py`**: (DEPRECATED) This FastAPI router was the original entry point for the orchestrator. It has been superseded by the endpoint in `MDSAPP/HQGTOPOS/api.py` and should be removed in the future.

## CONTEXT: Specialists
*   **`chat_agent.py`**: The primary user-facing agent for conversational interaction. It interprets user intent, manages dialogue, and can initiate missions or query the system. It leverages its LLM and tools to respond to user input and delegate tasks.
*   **`processor_agent.py`**: The "planner." This agent is responsible for **planning**. It takes a high-level mission brief and, using its LLM (powered by a refined prompt), generates a detailed, machine-executable `Workflow` object. This workflow outlines the sequence of tools and steps required.
*   **`executor_agent.py`**: The "doer." This agent is responsible for **execution**. It takes a `Workflow` or `EngineeredWorkflow` object and systematically executes its defined elements. It invokes the necessary `Tools` (via the `ToolRegistry`) and records the outcome of each step, producing a `WorkflowExecutionResult`.
*   **`engineer_agent.py`**: The "optimizer." This agent is responsible for **analysis and optimization**. It reviews the results of a completed workflow execution (the `Workflow` and its `WorkflowExecutionResult`) and, using its LLM (powered by a refined prompt), designs an optimized, reusable `EngineeredWorkflow`. This agent drives continuous improvement.

## Development Status / Roadmap

### Current Status:
*   The core `HQOrchestrator` flow (`Processor -> Executor -> Engineer`) is now fully LLM-driven and triggered via a robust, ADK-native API endpoint.
*   Prompts for `ProcessorAgent` and `EngineerAgent` have been refined for better output quality.
*   Basic integration tests for the HQ flow are in place (`tests/test_hq_flow.py`).

### Next Steps / Focus Areas:
*   **`ChatAgent` Enhancement**: Improve the `ChatAgent`'s ability to generate multiple datasets within a single `Casefile` object based on user input.
*   **`EngineerAgent` Tooling**: Provide the `EngineerAgent` with specific tools (e.g., for performance analysis) to enable more intelligent optimization decisions.
*   **Error Handling & Robustness**: Enhance error handling across all agents for more graceful failure and recovery.
*   **Advanced ADK Features**: Explore deeper integration of ADK `Memory` for long-term agent knowledge and `Callbacks` for fine-grained control and observability.
*   **Cleanup**: Remove the deprecated `api.py` from this module.


