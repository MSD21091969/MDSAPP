# Development Guidelines & Best Practices

This document outlines the best practices and guidelines for contributing to the MDS project. Adhering to these standards ensures code quality, consistency, and maintainability.

## 1. Testing

A robust testing suite is crucial for project stability. All new features should be accompanied by tests, and bug fixes should include a regression test.

*   **Framework**: We use `pytest` for testing.
*   **Location**: All tests are located in the `MDSAPP/tests/` directory.
*   **Unit Tests**: Each module should have corresponding unit tests that verify the functionality of individual classes and functions in isolation. Mocking should be used to isolate dependencies.
*   **Integration Tests**: These tests should verify the interaction between different components (e.g., an agent correctly using a manager, a manager correctly interacting with the database).
*   **Running Tests**: Tests can be run from the project root using `poetry run pytest`.

## Code Style & Quality

*   **Python**: Follow PEP 8 guidelines.
*   **Type Hinting**: Use type hints extensively for better code readability and maintainability.
*   **Docstrings**: Write clear and concise docstrings for all functions, classes, and modules.
*   **Error Handling**: Implement robust error handling.

## Testing Guidelines

Testing is a critical part of ensuring the quality and reliability of the MDS. We encourage a multi-layered testing approach:

### 1. Unit Tests
*   **Purpose**: To test individual components (e.g., a single agent's method, a manager function, a tool) in isolation.
*   **Focus**: Verify that each unit of code behaves as expected under various conditions.
*   **Location**: Place unit tests in `tests/` directory, typically in files named `test_your_module.py` (e.g., `tests/test_processor_agent.py`).
*   **Best Practices**: Use mocking (e.g., `unittest.mock`) to isolate the unit under test from its dependencies (LLMs, external services, other agents).

### 2. Integration Tests
*   **Purpose**: To verify the interactions and data flow between multiple components or agents.
*   **Focus**: Ensure that different parts of the system work correctly together, especially the orchestration flows.
*   **Location**: Place integration tests in `tests/` directory. For example, `tests/test_hq_flow.py` demonstrates how to test the entire `HQOrchestrator` flow.
*   **Best Practices**: Simulate the end-to-end flow as closely as possible, mocking external services (like LLMs) to ensure tests are fast and reliable.

### Running Tests
Always run all tests before committing your changes:
```bash
pytest
```

## Review Process

We enforce a consistent code style to ensure readability.

*   **Linter/Formatter**: We use `ruff` for both linting and formatting. It should be configured in `pyproject.toml`.
*   **CI/CD**: A CI/CD pipeline should automatically check for linting errors and test failures on every pull request.

## 3. Configuration Management

Configuration should be managed centrally and securely.

*   **Environment Variables**: Use a `.env` file for local development to store secrets and environment-specific settings.
*   **Structured Config**: For application-level configuration, consider using a Pydantic `BaseSettings` model in a central location like `MDSAPP/core/config.py` to load and validate settings from environment variables.

## 4. Documentation

*   **Docstrings**: All modules, classes, and public methods must have clear and concise docstrings explaining their purpose, arguments, and return values.
*   **Type Hinting**: The entire codebase must use full type hinting. This is checked by the linter and CI pipeline.
*   **Project Documentation**: All user-facing and architectural documentation is centralized in the `/docs` directory.

## 5. API Development

*   **Framework**: The API is built with `FastAPI`.
*   **Auto-documentation**: FastAPI provides automatic OpenAPI (Swagger) documentation. Ensure all API endpoints have clear descriptions and Pydantic models for request/response validation to make the generated documentation as useful as possible.

## 6. Dependency Management

*   **Manager**: Project dependencies are managed with `Poetry`.
*   **Adding Dependencies**: Use `poetry add <package_name>` for application dependencies and `poetry add --group dev <package_name>` for development dependencies.
*   **Lock File**: The `poetry.lock` file ensures deterministic builds and should always be committed to version control.
