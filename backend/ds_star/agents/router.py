"""Router agent for deciding whether to add steps or backtrack."""

from __future__ import annotations

import logging
import re

from ..core.agent import BaseAgent
from ..core.types import DSStarState, RouterDecision, RouterOutput
from ..prompts.templates import ROUTER_SYSTEM, ROUTER_USER
from ..providers.base import LLMProvider, Message


class RouterAgent(BaseAgent[None, RouterOutput]):
    """Agent that decides whether to add a new step or backtrack to fix errors."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
    ):
        """Initialize the router agent.

        Args:
            provider: LLM provider
            logger: Logger instance
        """
        super().__init__(provider, logger)

    @property
    def name(self) -> str:
        return "Router"

    def build_prompt(self, state: DSStarState, input_data: None) -> list[Message]:
        """Build prompt for routing decision.

        Args:
            state: Current session state
            input_data: Not used

        Returns:
            Messages for LLM
        """
        user_prompt = ROUTER_USER.format(
            query=state.query,
            steps=state.get_steps_text(),
            execution_result=state.get_execution_summary(),
            file_descriptions=state.get_file_descriptions_text(),
        )

        return [
            Message(role="system", content=ROUTER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> RouterOutput:
        """Parse LLM response into RouterOutput.

        Args:
            response: Raw LLM response

        Returns:
            RouterOutput with decision
        """
        response_upper = response.upper().strip()
        lines = response.strip().split("\n")
        first_line = lines[0].upper() if lines else ""

        # Extract reasoning (everything after first line)
        reasoning = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Check for ADD_STEP
        if "ADD_STEP" in first_line or "ADD STEP" in first_line:
            return RouterOutput(
                decision=RouterDecision.ADD_STEP,
                backtrack_to_step=None,
                reasoning=reasoning,
            )

        # Check for BACKTRACK:N pattern
        backtrack_match = re.search(r"BACKTRACK[:\s]*(\d+)", first_line)
        if backtrack_match:
            step_index = int(backtrack_match.group(1))
            return RouterOutput(
                decision=RouterDecision.BACKTRACK,
                backtrack_to_step=step_index,
                reasoning=reasoning,
            )

        # Check for "Step N is wrong" pattern
        step_wrong_match = re.search(r"STEP\s*(\d+)\s*(IS\s*)?(WRONG|INCORRECT|ERROR)", first_line)
        if step_wrong_match:
            step_index = int(step_wrong_match.group(1))
            return RouterOutput(
                decision=RouterDecision.BACKTRACK,
                backtrack_to_step=step_index,
                reasoning=reasoning,
            )

        # Default to ADD_STEP if unclear
        return RouterOutput(
            decision=RouterDecision.ADD_STEP,
            backtrack_to_step=None,
            reasoning=f"Could not parse response, defaulting to ADD_STEP. Original: {response[:200]}",
        )

    async def route(self, state: DSStarState) -> RouterOutput:
        """Determine the next action to take.

        Args:
            state: Current session state

        Returns:
            RouterOutput with decision
        """
        return await self.run(state, None)
