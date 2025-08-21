# Agents Module Context

This module contains all the AI agents. The files can be logically grouped as follows for future refactoring.

## CONTEXT: orchestration
*   `agents/hq_orchestrator.py`: The master orchestrator, implemented as a `CustomAgent`. It manages the full `Plan -> Execute -> Analyze` lifecycle for a given Casefile.
*   `agents/api.py`: The FastAPI router for agent-related actions, providing the endpoint to trigger the `HQOrchestrator`.

## CONTEXT: specialists
*   `agents/chat_agent.py`: The primary user-facing agent for conversational interaction.
*   `agents/processor_agent.py`: A tool-aware agent that designs a `Workflow` plan based on a mission and a list of available tools.
*   `agents/executor_agent.py`: A deterministic workflow engine that executes tools step-by-step based on a `Workflow` plan.
*   `agents/engineer_agent.py`: A two-stage analytical agent that first calculates execution metrics with a tool, then uses those metrics to design an optimized `EngineeredWorkflow`.