"""Finalizer agent for formatting the final output."""

from __future__ import annotations

import logging

from ..core.agent import BaseAgent
from ..core.types import DSStarState
from ..prompts.templates import FINALIZER_SYSTEM, FINALIZER_USER
from ..providers.base import LLMProvider, Message


class FinalizerAgent(BaseAgent[None, str]):
    """Agent that formats the final answer from execution results."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
        output_format: str | None = None,
    ):
        """Initialize the finalizer agent.

        Args:
            provider: LLM provider
            logger: Logger instance
            output_format: Optional format requirements (e.g., "round to 2 decimal places")
        """
        super().__init__(provider, logger)
        self.output_format = output_format or "Return the answer as-is"

    @property
    def name(self) -> str:
        return "Finalizer"

    def build_prompt(self, state: DSStarState, input_data: None) -> list[Message]:
        """Build prompt for output formatting.

        Args:
            state: Current session state
            input_data: Not used

        Returns:
            Messages for LLM
        """
        # Get execution result
        execution_result = state.get_execution_summary()

        user_prompt = FINALIZER_USER.format(
            query=state.query,
            execution_result=execution_result,
            output_format=self.output_format,
        )

        return [
            Message(role="system", content=FINALIZER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> str:
        """Parse LLM response into final answer.

        Args:
            response: Raw LLM response

        Returns:
            Formatted final answer
        """
        # Clean up the response
        answer = response.strip()

        # Remove common prefixes
        prefixes_to_remove = [
            "The answer is:",
            "Answer:",
            "Result:",
            "Final answer:",
            "RESULT:",
        ]

        for prefix in prefixes_to_remove:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix) :].strip()

        return answer

    async def finalize(self, state: DSStarState) -> str:
        """Generate the final formatted answer.

        Args:
            state: Current session state

        Returns:
            Formatted answer string
        """
        return await self.run(state, None)

    def extract_result_from_output(self, state: DSStarState) -> str | None:
        """Try to extract result directly from execution output.

        This is a fallback method that doesn't require an LLM call.

        Args:
            state: Current session state

        Returns:
            Extracted result or None if not found
        """
        if not state.last_execution_result:
            return None

        stdout = state.last_execution_result.stdout

        # Look for FINAL RESULT: section with separators
        if "FINAL RESULT:" in stdout:
            lines = stdout.split("\n")
            result_lines = []
            in_result_section = False

            for line in lines:
                if "FINAL RESULT:" in line:
                    in_result_section = True
                    continue
                elif in_result_section:
                    # Skip separator lines
                    if line.strip() == "=" * 50:
                        continue
                    # Stop at empty line after result
                    if not line.strip() and result_lines:
                        break
                    if line.strip():
                        result_lines.append(line)

            if result_lines:
                return "\n".join(result_lines)

        # Look for the last non-empty line
        lines = [l.strip() for l in stdout.split("\n") if l.strip() and l.strip() != "=" * 50]
        if lines:
            return lines[-1]

        return None
