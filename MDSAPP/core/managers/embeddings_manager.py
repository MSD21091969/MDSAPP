# MDSAPP/core/managers/embeddings_manager.py

import logging
from typing import List, TYPE_CHECKING
import os

# Updated imports
from MDSAPP.CasefileManagement.models.casefile import Casefile, DriveFileReference
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.utils.document_parser import DocumentParser
# Removed direct import: from MDSAPP.core.services.google_workspace_manager import GoogleWorkspaceManager

# Type hinting for GoogleWorkspaceManager
if TYPE_CHECKING:
    from MDSAPP.core.services.google_workspace_manager import GoogleWorkspaceManager

logger = logging.getLogger(__name__)

class EmbeddingsManager:
    """
    Manages the generation and storage of vector embeddings for documents.
    """
    def __init__(
        self,
        db_manager: DatabaseManager,
        parser: DocumentParser,
        google_workspace_manager: "GoogleWorkspaceManager" = None # Made optional
    ):
        self.db_manager = db_manager
        self.parser = parser
        self.google_workspace_manager = google_workspace_manager # Store the new dependency
        self.embedding_model = self.db_manager.embedding_model
        logger.info("EmbeddingsManager initialized.")

    def set_google_workspace_manager(self, google_workspace_manager: "GoogleWorkspaceManager"):
        """
        Injects the GoogleWorkspaceManager after initialization to resolve circular dependency.
        """
        self.google_workspace_manager = google_workspace_manager
        logger.info("GoogleWorkspaceManager injected into EmbeddingsManager.")
        
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]

    def generate_for_single_file(self, case_id: str, file_ref: DriveFileReference):
        """
        Generates and stores embeddings for a single file.
        """
        # Use google_workspace_manager to download the file
        if not self.google_workspace_manager:
            logger.error("GoogleWorkspaceManager is not available in EmbeddingsManager. Cannot download file.")
            return

        logger.info(f"Generating embeddings for file '{file_ref.name}' in case '{case_id}'.")
        
        temp_file_path = f"/tmp/{file_ref.id}"
        
        try:
            self.google_workspace_manager.download_file(file_ref.id, temp_file_path, file_ref.mime_type)
            
            text_content = self.parser.parse(temp_file_path)
            if not text_content:
                logger.warning(f"No text extracted from file '{file_ref.name}'. Skipping.")
                return

            chunks = self._chunk_text(text_content)
            
            for i, chunk in enumerate(chunks):
                if not self.embedding_model:
                    logger.error("Embedding model not available.")
                    break
                
                embedding = self.embedding_model.encode(chunk).tolist()
                
                chunk_data = {
                    "case_id": case_id,
                    "file_id": file_ref.id,
                    "file_name": file_ref.name,
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "embedding": embedding
                }
                self.db_manager.save_document_chunk(chunk_data)
                logger.info(f"Generated embedding for chunk {i} of file '{file_ref.name}'.")

        except Exception as e:
            logger.error(f"Failed to generate embeddings for file '{file_ref.name}': {e}", exc_info=True)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def generate_for_casefile(self, casefile: Casefile):
        logger.info(f"Starting embedding generation for all files in case '{casefile.id}'.")
        for file_ref in casefile.file_references:
            self.generate_for_single_file(casefile.id, file_ref)
