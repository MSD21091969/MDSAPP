# MDSAPP/core/managers/prompt_manager.py

import logging
from typing import Dict, Any
from jinja2 import Environment

from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.models.prompts import Prompt

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages loading, versioning, and rendering of prompts from Firestore.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._prompts: Dict[str, Prompt] = {}
        self._jinja_env = Environment()
        # No need to load prompts at init, can be loaded on demand or with a dedicated method.

    async def load_prompts_from_db(self):
        """
        Loads all prompt definitions from the Firestore database.
        """
        logger.info("Loading all prompts from Firestore...")
        try:
            prompts = await self.db_manager.load_all_prompts()
            for prompt in prompts:
                # Store prompts by a unique key, e.g., "agent_name-task_name"
                prompt_key = f"{prompt.agent_name}-{prompt.task_name}"
                # If there are multiple versions, only keep the latest one
                if prompt_key not in self._prompts or prompt.version > self._prompts[prompt_key].version:
                    self._prompts[prompt_key] = prompt
            logger.info(f"Successfully loaded {len(self._prompts)} latest version prompts.")
        except Exception as e:
            logger.error(f"Error loading prompts from Firestore: {e}", exc_info=True)

    def get_prompt(self, agent_name: str, task_name: str) -> Prompt | None:
        """
        Returns the latest version of a prompt for a specific agent and task.
        """
        prompt_key = f"{agent_name}-{task_name}"
        prompt = self._prompts.get(prompt_key)
        if not prompt:
            logger.warning(f"No prompt found for agent '{agent_name}' and task '{task_name}'.")
        return prompt

    def render_prompt(self, agent_name: str, task_name: str, context: Dict[str, Any]) -> str | None:
        """
        Renders a prompt with the given context.
        """
        prompt = self.get_prompt(agent_name, task_name)
        if not prompt:
            return None
        
        template = self._jinja_env.from_string(prompt.template)
        return template.render(context)