# MDSAPP/core/services/google_api_mock.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MockGoogleDriveService:
    """
    A mock class that simulates the Google Drive API service.
    Used for development and testing purposes.
    """
    def __init__(self):
        self.files = {
            "file-123": {"name": "document.pdf", "id": "file-123", "mimeType": "application/pdf", "web_view_link": "mock_link_pdf", "icon_link": "mock_icon_pdf", "path": "/mock/path/pdf"},
            "file-456": {"name": "spreadsheet.xlsx", "id": "file-456", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "web_view_link": "mock_link_xlsx", "icon_link": "mock_icon_xlsx", "path": "/mock/path/xlsx"},
        }
        logger.info("MockGoogleDriveService initialized.")

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        metadata = self.files.get(file_id)
        if not metadata:
            raise ValueError(f"File with ID '{file_id}' not found in mock service.")
        logger.info(f"MockGoogleDriveService: Retrieved metadata for file '{file_id}'.")
        return metadata

    def download_file(self, file_id: str, destination_path: str, mime_type: str):
        logger.info(f"Simulating download of file '{file_id}' to '{destination_path}'.")
        with open(destination_path, 'w') as f:
            f.write(f"This is mock content for file {file_id} with mimetype {mime_type}.")
