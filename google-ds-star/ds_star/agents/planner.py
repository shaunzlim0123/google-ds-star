"""Planner agent for generating analysis steps."""

from __future__ import annotations

import logging

from ..core.agent import BaseAgent
from ..core.types import DSStarState, Step, StepStatus
from ..prompts.templates import PLANNER_SYSTEM, PLANNER_USER
from ..providers.base import LLMProvider, Message


class PlannerAgent(BaseAgent[None, Step]):
    """Agent that generates the next step in the analysis plan."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
    ):
        """Initialize the planner agent.

        Args:
            provider: LLM provider
            logger: Logger instance
        """
        super().__init__(provider, logger)

    @property
    def name(self) -> str:
        return "Planner"

    def build_prompt(self, state: DSStarState, input_data: None) -> list[Message]:
        """Build prompt for step generation.

        Args:
            state: Current session state
            input_data: Not used

        Returns:
            Messages for LLM
        """
        # Format current steps
        if state.current_plan:
            current_steps = state.get_steps_text()
        else:
            current_steps = "No steps yet. Generate the first step."

        # Format execution result
        if state.last_execution_result:
            execution_result = state.get_execution_summary()
        else:
            execution_result = "No execution yet."

        user_prompt = PLANNER_USER.format(
            query=state.query,
            file_descriptions=state.get_file_descriptions_text(),
            current_steps=current_steps,
            execution_result=execution_result,
        )

        return [
            Message(role="system", content=PLANNER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> Step:
        """Parse LLM response into a Step.

        Args:
            response: Raw LLM response

        Returns:
            Step object
        """
        # Clean up the response
        step_description = response.strip()

        # Remove any markdown formatting
        if step_description.startswith("- "):
            step_description = step_description[2:]
        if step_description.startswith("* "):
            step_description = step_description[2:]

        # Remove step numbering if present
        parts = step_description.split(":", 1)
        if len(parts) > 1 and parts[0].lower().startswith("step"):
            step_description = parts[1].strip()

        return Step(
            index=-1,  # Will be set by caller
            description=step_description,
            status=StepStatus.PENDING,
        )

    async def generate_step(self, state: DSStarState) -> Step:
        """Generate the next step for the current state.

        Args:
            state: Current session state

        Returns:
            New step to add to the plan
        """
        step = await self.run(state, None)

        # Set the correct index
        step.index = len(state.current_plan)

        return step
