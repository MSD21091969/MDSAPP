# MDSAPP/core/services/retriever.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Retriever(ABC):
    """
    Abstract base class for all Retriever components in the MDS.
    Defines the contract for retrieving contextual information
    for Retrieval-Augmented Generation (RAG).
    """

    @abstractmethod
    def retrieve(self, query: str, casefile_id: str, top_k: int = 5) -> str:
        """
        Retrieves the most relevant context for a given query and casefile
        and formats it as a single string for the LLM prompt.

        Args:
            query (str): The search term or user question.
            casefile_id (str): The ID of the active Casefile.
            top_k (int): The maximum number of contextual chunks to return.

        Returns:
            str: A formatted string with the found context.
        """
        pass

    @abstractmethod
    def _register_tools(self, tool_registry: Any):
        """
        Registers the specific search and retrieval methods as tools
        in the central ToolRegistry.
        """
        pass
