# MDSAPP/agents/processor_agent.py

import logging
import json
from typing import AsyncGenerator, Dict, Any

from typing_extensions import override
from pydantic import PrivateAttr, ValidationError

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerationConfig

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.core.services.retriever import Retriever
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import Workflow
from MDSAPP.core.utils.llm_parser import parse_llm_json_output

logger = logging.getLogger(__name__)

class ProcessorAgent(BaseAgent):
    """
    Specialist agent that creates a `Workflow` object from a mission brief.
    Its sole responsibility is to generate the workflow JSON.
    """
    _model: GenerativeModel = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _retriever: Retriever = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        model: GenerativeModel,
        prompt_manager: PromptManager,
        retriever: Retriever,
        tool_registry: ToolRegistry,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._model = model
        self._prompt_manager = prompt_manager
        self._retriever = retriever
        self._tool_registry = tool_registry
        logger.info(f"ProcessorAgent initialized with model: {self._model._model_name}")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        The core logic for the ProcessorAgent. It uses an LLM to generate a
        `Workflow` object based on a given mission.
        """
        mission = ctx.session.state.get("mission", "")
        if not mission:
            yield Event(author=self.name, content="Error: Mission not found in session state.")
            return

        logger.info(f"ProcessorAgent: Generating workflow for mission: {mission[:50]}...")

        try:
            # 1. Get the prompt template
            prompt_config = self._prompt_manager.get_prompt_definition("PROCESSOR")
            if not prompt_config:
                yield Event(author=self.name, content=genai_types.Content(role="model", parts=[genai_types.Part(text="Error: Could not retrieve PROCESSOR prompt.")]))
                return
            
            # 2. Get available tools to provide them as context to the LLM
            tool_declarations = self._tool_registry.get_all_tool_declarations()
            tools_json_str = json.dumps([t.to_dict() for t in tool_declarations], indent=2)

            # 3. Format the prompt with the mission and available tools
            prompt = prompt_config.system_prompt.format(
                mission=mission,
                available_tools=tools_json_str,
                json_schema=Workflow.model_json_schema()
            )

            # 4. Call the generative model
            response = await self._model.generate_content_async(
                [prompt],
                generation_config=GenerationConfig(
                    response_mime_type="application/json",
                    max_output_tokens=16384
                )
            )
            
            # 5. Parse and validate the output
            try:
                llm_output = response.text
            except ValueError as e:
                logger.error(f"Error accessing response.text: {e}")
                if response.candidates:
                    for i, candidate in enumerate(response.candidates):
                        logger.error(f"Candidate {i} safety ratings: {candidate.safety_ratings}")
                        logger.error(f"Candidate {i} finish_reason: {candidate.finish_reason}")
                raise # Re-raise the exception after logging
            
            logger.debug(f"LLM Raw Output:\n{llm_output}")
            
            workflow_dict = parse_llm_json_output(llm_output)
            workflow_obj = Workflow.model_validate(workflow_dict)
            workflow_json = workflow_obj.model_dump_json()

            # 6. Yield the final event
            yield Event(
                author=self.name,
                content=genai_types.Content(role="model", parts=[genai_types.Part(text=workflow_json)])
            )
            logger.info(f"ProcessorAgent: Successfully generated and validated workflow_id: {workflow_obj.workflow_id}")

        except ValidationError as e:
            error_message = f"Failed to validate the generated workflow from LLM. Details: {e}"
            logger.error(error_message, exc_info=True)
            yield Event(author=self.name, content=genai_types.Content(role="model", parts=[genai_types.Part(text=error_message)]))
        except Exception as e:
            error_message = f"An unexpected error occurred during workflow generation: {e}"
            logger.error(error_message, exc_info=True)
            yield Event(author=self.name, content=genai_types.Content(role="model", parts=[genai_types.Part(text=error_message)]))
