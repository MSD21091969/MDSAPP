# HQGTOPOS Module Context

This module represents the highest level of orchestration and context within the MDS. It serves as the central command and control for the entire application, providing the overarching framework and entry points for mission management.

## CONTEXT: Top-Level Orchestration
*   **`manager.py`**: Contains the `run_hq_flow` function, which is the primary entry point for initiating a full mission lifecycle. It sets up the required agents and uses the ADK `Runner` to execute the `HQOrchestratorAgent`.
*   **`api.py`**: Defines the FastAPI router and the `/api/v1/hq/run/{casefile_id}` endpoint, which exposes the `run_hq_flow` function to the rest of the application and external clients.
*   This module conceptually houses the `HQOrchestratorAgent` (though its code resides in `MDSAPP/agents/`), which is the primary driver of the `Mission -> Plan -> Execute -> Analyze` lifecycle.

## Development Status / Roadmap

### Current Status:
*   The `HQOrchestratorAgent` is functional and serves as the central orchestrator for the full `Mission -> Plan -> Execute -> Analyze` lifecycle.
*   A dedicated API endpoint (`/api/v1/hq/run/{casefile_id}`) is implemented for triggering the HQ flow.
*   The `run_hq_flow` manager function provides a robust, ADK-native method for running the end-to-end orchestration.

### Next Steps / Focus Areas:
*   **Full HQ Flow Implementation:** Focus on completing the end-to-end implementation of the HQ orchestration flow, including seamless integration with all sub-agents and managers.
*   **Robust Error Handling and Recovery:** Enhance the HQ orchestrator's ability to handle errors gracefully and implement recovery mechanisms for long-running missions.
*   **Observability and Monitoring:** Integrate with advanced observability tools to provide real-time insights into mission progress and agent interactions.
*   **Global Configuration**: Centralize global application configurations and parameters relevant to top-level orchestration.
*   **Mission Prioritization**: Explore mechanisms for mission prioritization and scheduling within the HQGTOPOS framework.
*   **Dashboard/Monitoring Integration**: Integrate with high-level dashboards or monitoring tools to provide an overview of all active missions and their statuses.


