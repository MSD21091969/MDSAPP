# Workflow Management Module Context

This module is fundamental to the MDS, providing the core data structures for defining abstract, platform-agnostic workflows. It underpins the operations of the `ProcessorAgent` (which defines workflows) and the platform-specific `Executor` (which translates and runs them).

## CONTEXT: Workflow Data Models
*   **`models/workflow.py`**: Defines the core Pydantic data structures for the abstract workflow blueprints, including:
    *   `Workflow` / `EngineeredWorkflow`: These objects represent a logical plan. They are **not** directly executable. They are platform-agnostic blueprints created by the `ProcessorAgent` or `EngineerAgent`.
    *   `Element`: Represents a single unit of work (an agent, a tool) in the blueprint.
    *   `WorkflowDynamics`: The crucial "ADK link." This defines the workflow's logic as a Directed Acyclic Graph (DAG). It is this abstract graph that a platform-specific `Executor` (like the `ADK_Executor`) will parse and translate into a runnable process.
*   **`models/results.py`**: Defines data models for capturing the outcome of workflow executions, primarily `WorkflowExecutionResult`.

## Development Status / Roadmap

### Current Status:
*   Core data models (`Workflow`, `EngineeredWorkflow`) are well-defined as platform-agnostic blueprints.
*   The architectural role of the `Executor` has been clarified: it is a platform-specific component responsible for translating the abstract `WorkflowDynamics` graph into an executable flow.

### Next Steps / Focus Areas:
*   **Implement the `ADK_Executor`:** The primary focus is to build out the `ADK_Executor`'s translation logic. This involves writing the graph traversal code that can parse the `WorkflowDynamics` and correctly compose the corresponding ADK agents (`SequentialAgent`, `ParallelAgent`, custom conditional agents, etc.).
*   **Workflow Versioning**: Implement robust versioning for `Workflow` and `EngineeredWorkflow` blueprints to track changes and enable rollbacks.
*   **Workflow Validation**: Enhance validation logic to ensure the `ProcessorAgent` and `EngineerAgent` produce `Workflow` objects with valid, executable graph structures in `WorkflowDynamics`.

## Recent Updates (August 2025)
*   **Robust Workflow Generation:** Addressed Pydantic validation errors in `Workflow` models, ensuring the `ProcessorAgent` can reliably generate and self-correct workflow definitions. This involved refining the `WorkflowCondition` model and enhancing the `llm_parser` to provide detailed error feedback to the LLM during self-correction.
*   **EngineerAgent Extension:** The `EngineerAgent` has been extended with a `produce_dataset` tool, enabling it to initiate dataset production processes for casefiles.