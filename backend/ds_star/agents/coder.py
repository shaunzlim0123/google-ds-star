"""Coder agent for implementing plan steps as Python code."""

from __future__ import annotations

import logging
import re

from ..core.agent import BaseAgent
from ..core.types import CodeBlock, DSStarState
from ..prompts.templates import CODER_SYSTEM, CODER_USER
from ..providers.base import LLMProvider, Message


class CoderAgent(BaseAgent[None, CodeBlock]):
    """Agent that implements plan steps as executable Python code."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
    ):
        """Initialize the coder agent.

        Args:
            provider: LLM provider
            logger: Logger instance
        """
        super().__init__(provider, logger, max_tokens=4096)

    @property
    def name(self) -> str:
        return "Coder"

    def build_prompt(self, state: DSStarState, input_data: None) -> list[Message]:
        """Build prompt for code generation.

        Args:
            state: Current session state
            input_data: Not used

        Returns:
            Messages for LLM
        """
        # Format steps to implement
        steps = "\n".join(
            f"{i + 1}. {step.description}" for i, step in enumerate(state.current_plan)
        )

        # Get previous code if any
        previous_code = state.current_code.code if state.current_code else "# No previous code"

        # Get execution result
        if state.last_execution_result:
            execution_result = state.get_execution_summary()
        else:
            execution_result = "No previous execution."

        user_prompt = CODER_USER.format(
            query=state.query,
            file_descriptions=state.get_file_descriptions_text(),
            steps=steps,
            previous_code=previous_code,
            execution_result=execution_result,
        )

        return [
            Message(role="system", content=CODER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> CodeBlock:
        """Parse LLM response into a CodeBlock.

        Args:
            response: Raw LLM response

        Returns:
            CodeBlock object
        """
        code = self._extract_code(response)

        return CodeBlock(
            code=code,
            step_indices=list(range(len(code.split("\n")))),  # Placeholder
        )

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Extracted Python code
        """
        # Try to extract code from markdown code block
        patterns = [
            r"```python\n(.*?)```",
            r"```py\n(.*?)```",
            r"```\n(.*?)```",
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no code block found, try to clean up the response
        # Remove common non-code prefixes
        lines = response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Skip explanation lines
            if line.strip().startswith("#") or in_code:
                code_lines.append(line)
                in_code = True
            elif line.strip().startswith("import ") or line.strip().startswith("from "):
                code_lines.append(line)
                in_code = True
            elif in_code:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines)

        # Last resort: return as-is
        return response

    async def generate_code(self, state: DSStarState) -> CodeBlock:
        """Generate code implementing all current steps.

        Args:
            state: Current session state

        Returns:
            CodeBlock with implementation
        """
        code_block = await self.run(state, None)
        code_block.step_indices = [s.index for s in state.current_plan]
        return code_block
