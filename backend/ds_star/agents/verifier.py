"""Verifier agent for checking if the plan is sufficient."""

from __future__ import annotations

import logging

from ..core.agent import BaseAgent
from ..core.types import DSStarState, VerificationResult
from ..prompts.templates import VERIFIER_SYSTEM, VERIFIER_USER
from ..providers.base import LLMProvider, Message


class VerifierAgent(BaseAgent[None, VerificationResult]):
    """Agent that verifies if the current plan sufficiently answers the query."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
    ):
        """Initialize the verifier agent.

        Args:
            provider: LLM provider
            logger: Logger instance
        """
        super().__init__(provider, logger)

    @property
    def name(self) -> str:
        return "Verifier"

    def build_prompt(self, state: DSStarState, input_data: None) -> list[Message]:
        """Build prompt for verification.

        Args:
            state: Current session state
            input_data: Not used

        Returns:
            Messages for LLM
        """
        # Format steps
        steps = state.get_steps_text()

        # Get current code
        code = state.current_code.code if state.current_code else "# No code generated"

        # Get execution result
        execution_result = state.get_execution_summary()

        user_prompt = VERIFIER_USER.format(
            query=state.query,
            steps=steps,
            code=code,
            execution_result=execution_result,
        )

        return [
            Message(role="system", content=VERIFIER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> VerificationResult:
        """Parse LLM response into VerificationResult.

        Args:
            response: Raw LLM response

        Returns:
            VerificationResult enum value
        """
        response_upper = response.upper().strip()

        # Check for SUFFICIENT/INSUFFICIENT at the start
        if response_upper.startswith("SUFFICIENT"):
            return VerificationResult.SUFFICIENT
        elif response_upper.startswith("INSUFFICIENT"):
            return VerificationResult.INSUFFICIENT

        # Check anywhere in response
        if "SUFFICIENT" in response_upper and "INSUFFICIENT" not in response_upper:
            return VerificationResult.SUFFICIENT

        # Default to insufficient if unclear
        return VerificationResult.INSUFFICIENT

    async def verify(self, state: DSStarState) -> tuple[VerificationResult, str]:
        """Verify if the current state is sufficient.

        Args:
            state: Current session state

        Returns:
            Tuple of (VerificationResult, reasoning string)
        """
        messages = self.build_prompt(state, None)
        response = await self.provider.complete(messages)

        result = self.parse_response(response.content)

        # Extract reasoning (everything after SUFFICIENT/INSUFFICIENT)
        reasoning = response.content
        for prefix in ["SUFFICIENT", "INSUFFICIENT"]:
            if reasoning.upper().startswith(prefix):
                reasoning = reasoning[len(prefix) :].strip()
                if reasoning.startswith(":"):
                    reasoning = reasoning[1:].strip()
                break

        return result, reasoning
