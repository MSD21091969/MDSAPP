# MDSAPP/core/services/google_workspace_manager.py

import logging
from typing import Dict, Any, List, TYPE_CHECKING
from MDSAPP.core.managers.tool_registry import ToolRegistry
from google.generativeai.types import FunctionDeclaration

# Updated imports for Casefile and DriveFileReference
from MDSAPP.CasefileManagement.models.casefile import Casefile, DriveFileReference
from MDSAPP.core.services.google_api_mock import MockGoogleDriveService # New import

# Type hinting for EmbeddingsManager and CasefileManager
if TYPE_CHECKING:
    from MDSAPP.core.managers.embeddings_manager import EmbeddingsManager
    from MDSAPP.CasefileManagement.manager import CasefileManager

logger = logging.getLogger(__name__)

class GoogleWorkspaceManager:
    """
    This class is responsible for managing authentication and tool registration
    for all Google Workspace APIs (e.g., Gmail, Drive, Keep).
    It takes specific service clients (mock or real) as dependencies.
    """
    def __init__(
        self,
        casefile_manager: "CasefileManager",
        embeddings_manager: "EmbeddingsManager",
        drive_service: MockGoogleDriveService # Injected dependency
    ):
        self.casefile_manager = casefile_manager
        self.embeddings_manager = embeddings_manager
        self.drive_service = drive_service # Injected
        try:
            self._authenticated = True
            logger.info("Successfully authenticated with Google Workspace.")
        except FileNotFoundError:
            self._authenticated = False
            logger.error("'credentials.json' not found. Cannot authenticate with Google Workspace.")
        except Exception as e:
            self._authenticated = False
            logger.error(f"GoogleWorkspaceManager: Authentication failed. Tools will not be available. Error: {e}", exc_info=True)

    def is_authenticated(self) -> bool:
        """
        Returns the authentication status.
        """
        return self._authenticated

    # --- Gmail related methods ---
    def get_email_tool(self, query: str) -> List[Dict[str, Any]]:
        """
        Tool to search and retrieve a list of emails from a user's inbox.
        """
        if not self.is_authenticated():
            return [{"status": "FAILED", "error": "Google Workspace is not authenticated."}]
        
        logger.info(f"Searching for emails with query: '{query}'")
        return [{"id": "email-123", "subject": "Mock Email", "snippet": "This is a test email."}]

    # --- Drive related methods ---
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Retrieves file metadata from Google Drive (or injected service).
        """
        return self.drive_service.get_file_metadata(file_id)

    def download_file(self, file_id: str, destination_path: str, mime_type: str):
        """
        Downloads a file from Google Drive (or injected service).
        """
        self.drive_service.download_file(file_id, destination_path, mime_type)

    def add_file_to_casefile_tool(self, casefile_id: str, file_id: str) -> Dict[str, Any]:
        """
        Tool that adds a file from Google Drive to a casefile and then
        immediately triggers the embedding generation for that file.
        """
        try:
            casefile = self.casefile_manager.load_casefile(casefile_id)
            if not casefile:
                return {"status": "FAILED", "error": f"Casefile '{casefile_id}' not found."}

            file_metadata = self.get_file_metadata(file_id)
            file_ref = DriveFileReference(**file_metadata)

            casefile.file_references.append(file_ref)
            self.casefile_manager.db_manager.save_casefile(casefile)
            logger.info(f"File reference '{file_ref.name}' added to casefile '{casefile.id}'.")

            logger.info(f"Directly triggering embedding generation for file: {file_ref.name}")
            self.embeddings_manager.generate_for_single_file(casefile.id, file_ref)
            
            return {
                "status": "SUCCESS",
                "message": f"File '{file_metadata['name']}' added and embeddings generated."
            }
        except Exception as e:
            logger.error(f"Error in 'add_file_to_casefile_tool': {e}", exc_info=True)
            return {"status": "FAILED", "error": str(e)}

    def register_tools(self, tool_registry: ToolRegistry):
        """
        Registers the tools provided by the GoogleWorkspaceManager.
        """
        if not self.is_authenticated():
            logger.warning("Authentication failed, skipping Google Workspace tool registration.")
            return

        # Register Gmail tool
        get_email_function = FunctionDeclaration(
            name="get_email_tool",
            description="Searches for emails in the user's inbox.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query for the emails."},
                },
                "required": ["query"],
            },
        )
        tool_registry.register_tool(
            tool_name="get_email_tool",
            tool_declaration=get_email_function,
            tool_handler=self.get_email_tool
        )

        # Register Drive tool
        add_file_function = FunctionDeclaration(
            name="add_file_to_casefile_tool",
            description="Adds a file with a given ID from Google Drive to a casefile and generates its embedding.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string"},
                    "file_id": {"type": "string"},
                },
                "required": ["casefile_id", "file_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="add_file_to_casefile_tool",
            tool_declaration=add_file_function,
            tool_handler=self.add_file_to_casefile_tool
        )
        logger.info("GoogleWorkspaceManager tools registered.")