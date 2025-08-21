# MDSAPP/core/managers/tool_registry.py

import logging
from typing import Dict, List, Callable, Any
from google.generativeai.types import FunctionDeclaration

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Manages the registration and retrieval of all tools in the application,
    including their FunctionDeclarations and their handler functions.
    This is designed to be compatible with ADK's tool handling.
    """
    def __init__(self):
        self._tool_declarations: Dict[str, FunctionDeclaration] = {}
        self._tool_handlers: Dict[str, Callable[..., Any]] = {}
        logger.info("ToolRegistry initialized.")

    def register_tool(
        self,
        tool_name: str,
        tool_declaration: FunctionDeclaration,
        tool_handler: Callable[..., Any]
    ):
        """
        Registers a tool, including its declaration and handler.
        
        Args:
            tool_name: The name of the tool to register.
            tool_declaration: The FunctionDeclaration object.
            tool_handler: The function that implements the tool's logic.
        """
        if tool_name in self._tool_declarations:
            logger.warning(f"Tool '{tool_name}' is already registered. Overwriting.")
        
        self._tool_declarations[tool_name] = tool_declaration
        self._tool_handlers[tool_name] = tool_handler
        logger.info(f"Tool '{tool_name}' successfully registered.")

    def get_all_tool_declarations(self) -> List[FunctionDeclaration]:
        """Returns a list of all registered FunctionDeclaration objects."""
        return list(self._tool_declarations.values())

    def get_tool_handler(self, tool_name: str) -> Callable[..., Any] | None:
        """Retrieves the handler function for a given tool name."""
        return self._tool_handlers.get(tool_name)
