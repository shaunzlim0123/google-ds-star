"""Sandboxed Python code execution."""

from __future__ import annotations

import asyncio
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from ..config import ExecutorConfig
from .types import CodeBlock, ExecutionResult


class CodeExecutor:
    """Sandboxed Python code execution via subprocess."""

    def __init__(self, config: ExecutorConfig | None = None):
        """Initialize the code executor.

        Args:
            config: Executor configuration. Uses defaults if not provided.
        """
        self.config = config or ExecutorConfig()

    async def execute(self, code_block: CodeBlock) -> ExecutionResult:
        """Execute Python code in an isolated subprocess.

        Args:
            code_block: Code to execute

        Returns:
            ExecutionResult with stdout, stderr, and status
        """
        # Validate code before execution
        validation_error = self._validate_code(code_block.code)
        if validation_error:
            return ExecutionResult(
                success=False,
                error_traceback=f"Code validation failed: {validation_error}",
            )

        # Create temporary file with the code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code_block.code)
            temp_path = Path(f.name)

        try:
            start_time = time.time()

            # Run code in subprocess
            result = await self._run_subprocess(temp_path)

            execution_time = (time.time() - start_time) * 1000

            return ExecutionResult(
                success=result["success"],
                stdout=result["stdout"],
                stderr=result["stderr"],
                error_traceback=result.get("traceback"),
                execution_time_ms=execution_time,
            )
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)

    async def _run_subprocess(self, script_path: Path) -> dict:
        """Run Python script in subprocess with timeout.

        Args:
            script_path: Path to the Python script

        Returns:
            Dict with success, stdout, stderr, and optional traceback
        """
        try:
            # Prepare working directory
            cwd = self.config.working_directory or script_path.parent

            # Run subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "",
                    "traceback": f"Execution timed out after {self.config.timeout_seconds} seconds",
                }

            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Truncate if too long
            if len(stdout_str) > self.config.max_output_length:
                stdout_str = (
                    stdout_str[: self.config.max_output_length]
                    + f"\n... [truncated, total {len(stdout_str)} chars]"
                )
            if len(stderr_str) > self.config.max_output_length:
                stderr_str = (
                    stderr_str[: self.config.max_output_length]
                    + f"\n... [truncated, total {len(stderr_str)} chars]"
                )

            success = process.returncode == 0

            return {
                "success": success,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "traceback": stderr_str if not success else None,
            }

        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "traceback": f"Execution error: {type(e).__name__}: {e}",
            }

    def _validate_code(self, code: str) -> str | None:
        """Validate code before execution.

        Args:
            code: Python code to validate

        Returns:
            Error message if validation fails, None if valid
        """
        # Check for blocked imports/patterns
        for blocked in self.config.blocked_imports:
            if blocked in code:
                return f"Blocked pattern found: {blocked}"

        # Try to parse the code
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            return f"Syntax error: {e}"

        return None

    def execute_sync(self, code_block: CodeBlock) -> ExecutionResult:
        """Synchronous wrapper for execute.

        Args:
            code_block: Code to execute

        Returns:
            ExecutionResult with stdout, stderr, and status
        """
        return asyncio.run(self.execute(code_block))
