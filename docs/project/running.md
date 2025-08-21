# Running the Application

The application is a FastAPI web server that provides both an API and a web-based user interface (the "Cockpit").

### Starting the Cockpit & API Server

To run the application, use `uvicorn` from the project root. This will start the web server, making the Cockpit UI and all API endpoints available.

```bash
poetry run uvicorn MDSAPP.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### Interacting with the Cockpit

Navigate to `http://127.0.0.1:8000` in your browser. From the Cockpit, you can:
*   Start a new mission.
*   View a list of all projects (`Casefiles`) and their real-time status.
*   Click on a project to inspect its detailed data, including plans, results, and analyses.

### Legacy ADK Commands

For direct agent testing without the full application server, the ADK's built-in commands can still be used, but this is not the primary way to run the application.

```bash
# For the development UI targeting a specific agent folder
poetry run adk web MDSAPP/agents/

# For terminal-based interaction
poetry run adk run MDSAPP/agents/
```
