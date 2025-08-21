# MDSAPP/core/services/drive_manager.py

import logging
from typing import Dict, Any, TYPE_CHECKING

# This allows us to import for type hinting without causing a circular import error
if TYPE_CHECKING:
    from MDSAPP.core.managers.embeddings_manager import EmbeddingsManager

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.core.services.google_api_mock import MockGoogleDriveService
from MDSAPP.CasefileManagement.models.casefile import DriveFileReference
from google.generativeai.types import FunctionDeclaration

logger = logging.getLogger(__name__)

class DriveManager:
    """
    Manages interactions with Google Drive and directly triggers embedding generation.
    """
    def __init__(self, casefile_manager: CasefileManager, embeddings_manager: "EmbeddingsManager"):
        self.casefile_manager = casefile_manager
        self.embeddings_manager = embeddings_manager
        self.drive_service = MockGoogleDriveService()
        logger.info("DriveManager (MDSAPP) initialized.")

    def add_file_to_casefile_tool(self, casefile_id: str, file_id: str) -> Dict[str, Any]:
        """
        Tool that adds a file from Google Drive to a casefile and then
        immediately triggers the embedding generation for that file.
        """
        try:
            casefile = self.casefile_manager.load_casefile(casefile_id)
            if not casefile:
                return {"status": "FAILED", "error": f"Casefile '{casefile_id}' not found."}

            file_metadata = self.drive_service.get_file_metadata(file_id)
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

    def download_file(self, file_id: str, destination_path: str, mime_type: str):
        logger.info(f"Simulating download of file '{file_id}' to '{destination_path}'.")
        with open(destination_path, 'w') as f:
            f.write(f"This is mock content for file {file_id} with mimetype {mime_type}.")

    def register_tools(self, tool_registry: ToolRegistry):
        add_file_function = FunctionDeclaration(
            name="add_file_to_casefile_tool",
            description="Adds a file with a given ID from Google Drive to a casefile and generates its embedding.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The ID of the casefile to add the file to."},
                    "file_id": {"type": "string", "description": "The ID of the file in Google Drive."},
                },
                "required": ["casefile_id", "file_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="add_file_to_casefile_tool",
            tool_declaration=add_file_function,
            tool_handler=self.add_file_to_casefile_tool
        )
        logger.info("DriveManager tools registered.")
