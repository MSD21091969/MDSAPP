# MDSAPP/main.py

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

with open("startup_check.log", "w") as f:
    f.write("main.py started\n")

# Load environment variables BEFORE any other application imports.
# This is crucial to ensure libraries like google.generativeai are configured correctly.
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routers from the new MDSAPP structure
from MDSAPP.CasefileManagement.api.v1 import router as casefile_router
from MDSAPP.CommunicationsManagement.api.v1 import router as chat_router
from MDSAPP.agents.api import router as agent_router
from MDSAPP.HQGTOPOS.api import router as hq_router
from MDSAPP.WorkFlowManagement.api.v1 import router as workflow_engineer_router
from MDSAPP.api.v1 import settings as settings_router

# Import dependencies from the new MDSAPP core
# Import dependencies from the new MDSAPP core
from MDSAPP.core.dependencies import get_tool_registry, register_all_tools, initialize_managers
from MDSAPP.core.logging_config import setup_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown tasks of the application.
    """
    setup_logging()
    logger.info("MDSAPP application starting up...")
    
    logger.info("Registering all tools...")
    tool_registry = get_tool_registry()
    register_all_tools(tool_registry)
    logger.info("Tool registration completed.")

    logger.info("Initializing managers...")
    initialize_managers()
    logger.info("Managers initialized.")
    
    yield
    
    logger.info("MDSAPP application shutting down.")

# Initialize the FastAPI application
app = FastAPI(
    title="MDS - Modular Data System (MDSAPP)",
    description="A self-learning orchestration platform for data analysis and processing.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "null", # This is for when index.html is opened directly from the file system
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from the new MDSAPP modules
app.include_router(casefile_router, prefix="/api/v1", tags=["Casefile Management"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agents"])
app.include_router(hq_router, prefix="/api/v1", tags=["HQ Orchestrator"])
app.include_router(workflow_engineer_router, prefix="/api/v1", tags=["Workflow Engineer"])
app.include_router(settings_router.router, prefix="/api/v1", tags=["Settings"])

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="MDSAPP/static"), name="static")

@app.get("/", tags=["System"])
async def read_root():
    """
    Redirects to the static HTML page.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")