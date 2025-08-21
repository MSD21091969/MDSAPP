# Recent Updates

## MDS7 Project Updates

### Mid-August 2025: Foundational Bug Fixes & Stability

A critical debugging session was completed, moving the application from a non-functional state to a stable, proof-of-concept prototype. Key accomplishments include:

*   **Application Startup Reliability:** Resolved a `NameError` on startup by correcting a missing import.
*   **Asynchronous Operations:** Fixed a core `AttributeError` related to an un-awaited coroutine (`load_casefile`), unblocking the entire agent orchestration flow.
*   **Data Integrity:** Corrected a major bug in the `CasefileManager` where sub-casefiles were not being saved independently, ensuring the integrity of the hierarchical casefile structure.

These fixes allow the application's core workflows to run successfully from end to end.

## Recent Platform Updates (Post-August 2025)

The Google Cloud ecosystem for agent development is rapidly evolving. Here are some notable recent updates:

### Google Agent Development Kit (ADK)

*   **ADK v1.11.0 (2025-08-14):**
    *   Added support for prefixes in tool names.
    *   Exposed a `print_detailed_results` parameter in `AgentEvaluator.evaluate`.
*   **ADK v1.10.0 (2025-08-07):**
    *   Implemented live session resumption.
*   **ADK v1.9.0 (2025-07-31):**
    *   Added a `-v` or `--verbose` flag to the CLI for enabling debug logging.
*   **New Versions (v1.2.0+):** Recent releases have focused on security and developer experience, such as making the `adk web` server default to `127.0.0.1`.
*   **Enhanced Security**: The `adk web` command now defaults to binding to `127.0.0.1` (localhost) for a more secure local development setup.
*   **Improved Developer Experience**: The ADK CLI provides more comprehensive help text when it receives invalid arguments. Additionally, numerous documentation strings (docstrings) have been improved for clarity.
*   **New Features & Integrations**:
    *   Support for deploying agents directly to the agent engine via the ADK CLI.
    *   Integration with Google Cloud Storage (GCS) for managing artifacts.
    *   Index tracking has been implemented to better manage parallel tool calls.
    *   A sample agent for connecting to Jira Cloud has been added.
*   **Java SDK:** The ADK is now fully supported in Java with an initial release of the Java ADK (v0.1.0).
*   **Python ADK**: The Python ADK reached a stable, production-ready v1.0.0 release.
*   **A2A Protocol**: The A2A (Agent-to-Agent) protocol was updated to support stateless interactions for more lightweight communication.
*   **Open Source Additions:** The ADK Web UI and the `MLE-STAR` (a sample ML engineering agent) are now open-sourced, providing more reference code.
*   **Gemini CLI Integration:** Tighter integration with the Gemini CLI helps streamline development and testing.
*   **Asynchronous Operations**: A fundamental change in version 1.0.0 was the shift to asynchronous operations for all core service interfaces, significantly improving performance for I/O-bound tasks.
*   **Code Execution**: The built-in code execution tool was renamed and moved, clarifying the distinction between "tools" (what an agent uses) and "executors" (how an agent performs actions).
*   **API Wire Format**: The JSON data format for the ADK API server changed from snake_case to camelCase, which may require updates to custom scripts.
*   **ADK Roadmap (Q3 2025):**
    *   **Configurable ADK:** An initiative to allow agent creation and definition through configuration specifications rather than code.
    *   **Computer Use Support:** Enabling ADK agents to utilize tools for browser access.
    *   **ADK GitHub Assistant:** The development of ADK agents specifically for managing the ADK community and its codebase.
    *   **Enhanced Evaluation:** Improvements to the ADK evaluation infrastructure to make it more pluggable and extensible with new metrics.

### Vertex AI Agent Engine & AI Applications

*   **General Availability:** The Agent Engine is now generally available (GA) and is a production-ready service.
*   **Product Renaming**: The broader "Vertex AI Agent Builder" suite has been renamed to **"AI Applications"** as of August 2025.
*   **New Preview Features:**
    *   **Memory Bank:** A new capability allowing agents to form and recall long-term memories from conversations.
    *   **Specialized Data Agents:** New agent types for automating data engineering (in BigQuery) and data science (in Colab Enterprise) tasks.
    *   **Custom Service Accounts:** Enhanced security by allowing agents to operate with a dedicated IAM service account.
    *   **Console Management:** You can now manage deployed agents and sessions directly from the Google Cloud Console.
*   **Expanded Model Support:** The Vertex AI Model Garden has expanded to include new models like Gemma 3, Imagen 4, and models from OpenAI.
*   **Agent Garden:** A library of pre-built, ready-to-use agent samples and patterns to help developers get started quickly.
*   **Broad Framework Support:** The Agent Engine offers flexibility by supporting multiple development frameworks, including LangChain, AutoGen 2, and LlamaIndex.

### Model Context Protocol (MCP)

*   **June 2025 Update (Protocol Version 2025-06-18):**
    *   **Enhanced Security with OAuth 2.0:** MCP servers are now classified as OAuth 2.0 Resource Servers.
    *   **Structured JSON Tool Output:** Tools can now produce structured JSON outputs based on a predefined schema.
    *   **Interactive User Input (Elicitation):** Servers can now pause a tool's operation and request additional information from the user.
    *   **Resource Linking:** Tools can now return a URI to a resource instead of embedding the entire resource in the response.
    *   **Removal of JSON-RPC Batching:** Support for batching multiple requests into a single message was removed.
*   **March 2025 Update (Protocol Version 2025-03-26):**
    *   **OAuth 2.1 Authorization Framework:** A comprehensive authorization framework based on the OAuth 2.1 draft was introduced.
    *   **Streamable HTTP Transport:** A more flexible "Streamable HTTP" transport replaced the previous HTTP+SSE method.
    *   **Support for Audio Data:** The protocol added support for audio data, in addition to the existing text and image types.

### AgentOps

*   **Platform Enhancements:**
    *   **Time Travel Debugging:** Allows for replaying and analyzing agent runs.
    *   **Cost Management:** Features for monitoring and visualizing spending on LLM tokens.
*   **Industry Adoption:**
    *   **Mainstream Adoption:** AgentOps principles are becoming standard for deploying reliable agentic systems.
    *   **Framework Integration:** Native integrations with leading agent frameworks like CrewAI and AutoGen.
