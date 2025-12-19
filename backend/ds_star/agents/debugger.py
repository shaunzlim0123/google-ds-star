"""Debugger agent for fixing failed code."""

from __future__ import annotations

import logging
import re

from ..core.agent import BaseAgent
from ..core.types import CodeBlock, DSStarState, ExecutionResult
from ..prompts.templates import DEBUGGER_SYSTEM, DEBUGGER_USER
from ..providers.base import LLMProvider, Message


class DebuggerAgent(BaseAgent[ExecutionResult, CodeBlock]):
    """Agent that fixes Python code that failed during execution."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
    ):
        """Initialize the debugger agent.

        Args:
            provider: LLM provider
            logger: Logger instance
        """
        super().__init__(provider, logger, max_tokens=4096)

    @property
    def name(self) -> str:
        return "Debugger"

    def build_prompt(
        self, state: DSStarState, failed_result: ExecutionResult
    ) -> list[Message]:
        """Build prompt for debugging.

        Args:
            state: Current session state
            failed_result: The execution result that failed

        Returns:
            Messages for LLM
        """
        # Get the code that failed
        code = state.current_code.code if state.current_code else "# No code available"

        # Get error traceback
        error_traceback = failed_result.error_traceback or failed_result.stderr or "Unknown error"

        user_prompt = DEBUGGER_USER.format(
            code=code,
            error_traceback=error_traceback,
            file_descriptions=state.get_file_descriptions_text(),
        )

        return [
            Message(role="system", content=DEBUGGER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> CodeBlock:
        """Parse LLM response into a CodeBlock.

        Args:
            response: Raw LLM response

        Returns:
            CodeBlock with fixed code
        """
        code = self._extract_code(response)

        return CodeBlock(
            code=code,
            step_indices=[],
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

        # If no code block, look for import statements as start
        lines = response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                in_code = True
            if in_code:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines)

        # Last resort: return as-is
        return response

    async def debug(
        self, state: DSStarState, failed_result: ExecutionResult
    ) -> CodeBlock:
        """Fix failed code.

        Args:
            state: Current session state
            failed_result: The execution result that failed

        Returns:
            CodeBlock with fixed code
        """
        fixed_code = await self.run(state, failed_result)

        # Preserve step indices from original code
        if state.current_code:
            fixed_code.step_indices = state.current_code.step_indices

        return fixed_code
