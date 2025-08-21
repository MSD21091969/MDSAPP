# MDSAPP/agents/engineer_agent.py

import logging
import json
from typing import AsyncGenerator

from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerationConfig

from MDSAPP.core.managers.prompt_manager import PromptManager
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.tool_registry import ToolRegistry
from MDSAPP.WorkFlowManagement.models.workflow import EngineeredWorkflow
from MDSAPP.core.utils.llm_parser import parse_llm_json_output

logger = logging.getLogger(__name__)

class EngineerAgent(BaseAgent):
    """
    Specialist meta-agent that analyzes results and creates optimized `EngineeredWorkflow` templates.
    """
    _model: GenerativeModel = PrivateAttr()
    _prompt_manager: PromptManager = PrivateAttr()
    _casefile_manager: CasefileManager = PrivateAttr()
    _tool_registry: ToolRegistry = PrivateAttr()

    def __init__(
        self,
        name: str,
        model: GenerativeModel,
        prompt_manager: PromptManager,
        casefile_manager: CasefileManager,
        tool_registry: ToolRegistry,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self._model = model
        self._prompt_manager = prompt_manager
        self._casefile_manager = casefile_manager
        self._tool_registry = tool_registry
        logger.info(f"EngineerAgent initialized with model: {self._model._model_name}")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        The core logic for the EngineerAgent. It uses an LLM to generate an
        `EngineeredWorkflow` based on a completed workflow execution.
        """
        casefile_id = ctx.session.state.get("casefile_id", "")
        if not casefile_id:
            yield Event(author=self.name, content="Error: casefile_id is required.")
            return

        casefile = self._casefile_manager.load_casefile(casefile_id)
        if not casefile:
            yield Event(author=self.name, content=f"Error: Casefile with ID '{casefile_id}' not found.")
            return

        if not casefile.workflows or not casefile.execution_results:
            yield Event(author=self.name, content=f"Error: Casefile '{casefile_id}' lacks a workflow and/or results to engineer.")
            return

        logger.info(f"EngineerAgent: Generating engineered workflow for casefile: {casefile_id}")

        try:
            # 1. Get the prompt template
            prompt_config = self._prompt_manager.get_prompt_definition("ENGINEER")
            if not prompt_config:
                yield Event(author=self.name, content="Error: Could not retrieve ENGINEER prompt.")
                return

            # 2. Consolidate context for the LLM
            original_workflow = casefile.workflows[0].model_dump_json(indent=2)
            execution_results = casefile.execution_results[0].model_dump_json(indent=2)
            tool_declarations = self._tool_registry.get_all_tool_declarations()
            tools_json_str = json.dumps([t.to_dict() for t in tool_declarations], indent=2)

            # 3. Format the prompt
            prompt = prompt_config.system_prompt.format(
                mission=casefile.mission,
                original_workflow=original_workflow,
                execution_results=execution_results,
                available_tools=tools_json_str,
                json_schema=EngineeredWorkflow.model_json_schema()
            )

            # 4. Call the generative model
            response = await self._model.generate_content_async(
                [prompt],
                generation_config=GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            # 5. Parse and validate the output
            llm_output = response.text
            logger.debug(f"LLM Raw Output:\n{llm_output}")

            eng_workflow_dict = parse_llm_json_output(llm_output)
            eng_workflow_obj = EngineeredWorkflow.model_validate(eng_workflow_dict)
            eng_workflow_json = eng_workflow_obj.model_dump_json()

            # 6. Yield the final event
            yield Event(
                author=self.name,
                content=genai_types.Content(role="model", parts=[genai_types.Part(text=eng_workflow_json)])
            )
            logger.info(f"EngineerAgent: Successfully generated and validated engineered_workflow_id: {eng_workflow_obj.engineered_workflow_id}")

        except ValidationError as e:
            error_message = f"Failed to validate the generated workflow from LLM. Details: {e}"
            logger.error(error_message, exc_info=True)
            yield Event(author=self.name, content=genai_types.Content(role="model", parts=[genai_types.Part(text=error_message)]))
        except Exception as e:
            error_message = f"An unexpected error occurred during workflow engineering: {e}"
            logger.error(error_message, exc_info=True)
            yield Event(author=self.name, content=genai_types.Content(role="model", parts=[genai_types.Part(text=error_message)]))
