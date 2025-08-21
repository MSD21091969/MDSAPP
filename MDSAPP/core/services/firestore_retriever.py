# MDSAPP/core/services/firestore_retriever.py

import logging
from typing import List

from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from google.generativeai.types import FunctionDeclaration

from MDSAPP.core.services.retriever import Retriever # Updated import
from MDSAPP.core.managers.database_manager import DatabaseManager # Updated import
from MDSAPP.core.managers.tool_registry import ToolRegistry # Updated import

logger = logging.getLogger(__name__)

class FirestoreRetriever(Retriever):
    """
    Concrete implementation of the Retriever that uses Firestore's
    vector search capabilities.
    """
    def __init__(self, db_manager: DatabaseManager):
        """
        Initializes the retriever with a dependency to the DatabaseManager.
        """
        self.db_manager = db_manager
        logger.info("FirestoreRetriever initialized with DatabaseManager.")

    def retrieve(self, query: str, casefile_id: str, top_k: int = 5) -> str:
        """
        Public method that calls the RAG functionality and returns a
        formatted context string.
        """
        if not casefile_id:
            return "Info: No casefile is currently active. Cannot retrieve context."
            
        return self.find_relevant_document_chunks(
            case_id=casefile_id,
            query_text=query,
            limit=top_k
        )

    def _register_tools(self, tool_registry: ToolRegistry):
        """Registers the RAG search function as a tool."""
        query_content_function = FunctionDeclaration(
            name="query_document_content",
            description="Searches the content of documents and returns relevant fragments.",
            parameters={
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "query_text": {"type": "string"}
                },
                "required": ["case_id", "query_text"]
            },
        )
        # Assuming tool_registry.register_tool now takes a handler
        tool_registry.register_tool(
            tool_name="query_document_content",
            tool_declaration=query_content_function,
            tool_handler=self.find_relevant_document_chunks # Register the method as handler
        )
        logger.info("Tool 'query_document_content' successfully registered.")

    def find_relevant_document_chunks(self, case_id: str, query_text: str, limit: int = 5) -> str:
        """
        Performs the vector search and formats the results as a string.
        """
        if not self.db_manager.db or not self.db_manager.embedding_model:
            return "Info: Database or embedding model not available for search."
        
        try:
            query_embedding = self.db_manager.embedding_model.encode(query_text).tolist()
            
            # Firestore's find_nearest doesn't support filtering, so we fetch more results
            # and filter them in the application. This is a workaround.
            # A better long-term solution is to have a separate document_chunks
            # collection for each casefile.
            firestore_query = self.db_manager.db.collection(self.db_manager.documents_collection_name).find_nearest(
                vector_field='embedding',
                query_vector=Vector(query_embedding),
                limit=50, # Fetch more to filter from
                distance_measure=DistanceMeasure.COSINE
            )
            
            all_docs = [doc.to_dict() for doc in firestore_query.get()]
            
            # Filter the documents by case_id
            docs = [doc for doc in all_docs if doc.get('case_id') == case_id][:limit]

            if not docs:
                return "No relevant information found in the case documents."
            
            context_str = "Relevant excerpts from documents:\n"
            for data in docs:
                context_str += f"- From document '{data.get('file_name', 'unknown')}': \"...{data.get('chunk_text', '')}...\"\n"
            
            return context_str

        except Exception as e:
            logger.error(f"Error during vector search for case '{case_id}': {e}", exc_info=True)
            return "An error occurred while searching the documents."

