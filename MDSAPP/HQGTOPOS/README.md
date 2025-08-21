# HQGTOPOS - The MDS Orchestrator

This module contains the `hqflow`, the central command and control system for the MDS application.

## Purpose

The `hqflow` is the master workflow responsible for overseeing the entire lifecycle of a mission, from initial planning to final analysis. It does not perform the tasks itself but instead delegates them to the appropriate specialized agents (`ProcessorAgent`, `ExecutorAgent`, `EngineerAgent`).

## Architecture

The `hqflow` operates on a `Casefile` object. It examines the state of the `Casefile` to determine the next logical step in the event loop.

The typical flow is as follows:

1.  **Trigger the `hqflow`**: The `hqflow` is triggered by the `/api/v1/hq/run/{casefile_id}` endpoint.
2.  **Receive Casefile**: The `hqflow` is triggered with a `Casefile` that contains a new user-defined `mission`.
3.  **Delegate to Processor**: It calls the `ProcessorAgent` to create a `Workflow` based on the `mission`.
4.  **Delegate to Executor**: Once the `Workflow` is created, it calls the `ExecutorAgent` to execute it.
5.  **Delegate to Engineer**: After successful execution, it calls the `EngineerAgent` to analyze the results and create an `EngineeredWorkflow`.

The `hqflow` is the brain of the MDS, ensuring that the right agent is performing the right task at the right time.


