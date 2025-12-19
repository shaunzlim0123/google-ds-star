"""Main DS-STAR session orchestrator implementing Algorithm 1."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Callable, Awaitable

from ..agents.analyzer import AnalyzerAgent
from ..agents.coder import CoderAgent
from ..agents.debugger import DebuggerAgent
from ..agents.finalizer import FinalizerAgent
from ..agents.planner import PlannerAgent
from ..agents.router import RouterAgent
from ..agents.verifier import VerifierAgent
from ..config import DSStarConfig, ExecutorConfig
from ..providers.base import LLMProvider
from ..utils.logging import setup_logger
from .executor import CodeExecutor
from .types import (
    DSStarState,
    FileDescription,
    RouterDecision,
    StepStatus,
    VerificationResult,
)


class DSStarSession:
    """Main orchestration class implementing DS-STAR Algorithm 1.

    This class coordinates all agents to solve data science problems through
    iterative planning and verification.
    """

    def __init__(
        self,
        provider: LLMProvider,
        config: DSStarConfig | None = None,
        executor: CodeExecutor | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialize a DS-STAR session.

        Args:
            provider: LLM provider for agent calls
            config: Session configuration
            executor: Code executor (creates default if not provided)
            logger: Logger instance
        """
        self.provider = provider
        self.config = config or DSStarConfig()
        self.logger = logger or setup_logger("ds_star", self.config.log_level)

        # Initialize executor
        executor_config = ExecutorConfig(
            timeout_seconds=self.config.execution_timeout_seconds,
            max_output_length=self.config.max_output_length,
        )
        self.executor = executor or CodeExecutor(executor_config)

        # Initialize agents
        self.analyzer = AnalyzerAgent(provider, self.logger)
        self.planner = PlannerAgent(provider, self.logger)
        self.coder = CoderAgent(provider, self.logger)
        self.verifier = VerifierAgent(provider, self.logger)
        self.router = RouterAgent(provider, self.logger)
        self.debugger = DebuggerAgent(provider, self.logger)
        self.finalizer = FinalizerAgent(
            provider, self.logger, self.config.output_format
        )

        # Track state for run_with_state()
        self._current_state: DSStarState | None = None

    async def run(
        self,
        query: str,
        data_files: list[str],
        on_step: Callable[[DSStarState], Awaitable[None]] | None = None,
    ) -> str:
        """Execute DS-STAR algorithm to answer a data science query.

        Args:
            query: User's data science question
            data_files: Paths to data files (can include directories)
            on_step: Optional callback after each iteration

        Returns:
            Final answer string
        """
        self.logger.info(f"Starting DS-STAR session for query: {query}...")

        # Expand directories and filter files
        all_files = self._expand_file_paths(data_files)
        self.logger.info(f"Found {len(all_files)} data files")

        # Initialize state and store reference
        state = DSStarState(query=query, data_files=all_files)
        self._current_state = state

        # Phase 1: Analyze all data files
        self.logger.info("Phase 1: Analyzing data files...")
        state.file_descriptions = await self._analyze_files(all_files)
        self.logger.info(f"Analyzed {len(state.file_descriptions)} files")

        # Phase 2: Iterative planning loop
        self.logger.info("Phase 2: Iterative planning and verification...")

        for iteration in range(self.config.max_iterations):
            state.iteration = iteration
            self.logger.info(f"=== Iteration {iteration + 1} ===")

            # Generate next step
            step = await self.planner.generate_step(state)
            state.steps.append(step)
            self.logger.info(f"New step: {step.description}")

            # Generate code for all current steps
            state.current_code = await self.coder.generate_code(state)

            # Execute with debugging
            result = await self._execute_with_debug(state)
            state.execution_results.append(result)

            # Mark step as completed or failed
            step.status = StepStatus.COMPLETED if result.success else StepStatus.FAILED

            # Verify sufficiency
            verification, reasoning = await self.verifier.verify(state)
            self.logger.info(f"Verification: {verification.value} - {reasoning}")

            if verification == VerificationResult.SUFFICIENT:
                state.is_complete = True
                self.logger.info("Plan verified as sufficient!")
                break

            # Route: decide next action
            router_output = await self.router.route(state)
            self.logger.info(
                f"Router decision: {router_output.decision.value}"
                + (
                    f" (backtrack to step {router_output.backtrack_to_step})"
                    if router_output.backtrack_to_step is not None
                    else ""
                )
            )

            if router_output.decision == RouterDecision.BACKTRACK:
                self._backtrack(state, router_output.backtrack_to_step or 0)

            # Call progress callback if provided
            if on_step:
                await on_step(state)

        # Phase 3: Finalize output
        self.logger.info("Phase 3: Finalizing output...")

        # Try to extract result directly first
        direct_result = self.finalizer.extract_result_from_output(state)
        if direct_result:
            state.final_answer = direct_result
        else:
            state.final_answer = await self.finalizer.finalize(state)

        self.logger.info(f"Final answer generated.")
        return state.final_answer

    async def run_with_state(
        self,
        query: str,
        data_files: list[str],
        on_step: Callable[[DSStarState], Awaitable[None]] | None = None,
    ) -> DSStarState:
        """Execute DS-STAR and return full state.

        Same as run() but returns the complete state object for inspection.

        Args:
            query: User's data science question
            data_files: Paths to data files
            on_step: Optional callback after each iteration

        Returns:
            Complete DSStarState object
        """
        # Run the algorithm (state is stored in self._current_state)
        await self.run(query, data_files, on_step)

        # Return the populated state
        return self._current_state

    async def _analyze_files(self, files: list[str]) -> list[FileDescription]:
        """Analyze all data files in parallel.

        Args:
            files: List of file paths

        Returns:
            List of FileDescription objects
        """
        # Limit concurrency to avoid rate limits
        semaphore = asyncio.Semaphore(5)

        async def analyze_with_semaphore(file_path: str) -> FileDescription:
            async with semaphore:
                return await self.analyzer.analyze_file(file_path)

        # Analyze all files concurrently
        tasks = [analyze_with_semaphore(f) for f in files]
        descriptions = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures
        valid_descriptions = []
        for desc, file_path in zip(descriptions, files):
            if isinstance(desc, Exception):
                self.logger.warning(f"Failed to analyze {file_path}: {desc}")
            else:
                valid_descriptions.append(desc)

        return valid_descriptions

    async def _execute_with_debug(self, state: DSStarState):
        """Execute code with automatic debugging on failure.

        Args:
            state: Current session state

        Returns:
            ExecutionResult from successful execution or last attempt
        """
        if not state.current_code:
            from .types import ExecutionResult

            return ExecutionResult(
                success=False, error_traceback="No code to execute"
            )

        for attempt in range(self.config.max_debug_attempts):
            result = await self.executor.execute(state.current_code)

            if result.success:
                self.logger.debug(f"Execution succeeded on attempt {attempt + 1}")
                return result

            self.logger.warning(
                f"Execution failed (attempt {attempt + 1}/{self.config.max_debug_attempts})"
            )

            # Try to debug if we have attempts left
            if attempt < self.config.max_debug_attempts - 1:
                self.logger.info("Attempting to debug...")
                state.current_code = await self.debugger.debug(state, result)

        return result

    def _backtrack(self, state: DSStarState, to_step: int) -> None:
        """Remove steps from to_step onwards.

        Args:
            state: Current session state
            to_step: Step index to backtrack to (steps >= to_step are removed)
        """
        # Mark steps as backtracked
        for step in state.steps:
            if step.index >= to_step:
                step.status = StepStatus.BACKTRACKED

        self.logger.info(
            f"Backtracked: removed {len([s for s in state.steps if s.status == StepStatus.BACKTRACKED])} steps"
        )

    def _expand_file_paths(self, paths: list[str]) -> list[str]:
        """Expand directories and filter to allowed extensions.

        Args:
            paths: List of file or directory paths

        Returns:
            List of individual file paths
        """
        all_files = []

        for path_str in paths:
            path = Path(path_str)

            if path.is_file():
                if self._is_allowed_file(path):
                    all_files.append(str(path))
            elif path.is_dir():
                # Recursively find all files
                for file_path in path.rglob("*"):
                    if file_path.is_file() and self._is_allowed_file(file_path):
                        all_files.append(str(file_path))

        return all_files

    def _is_allowed_file(self, path: Path) -> bool:
        """Check if file extension is allowed.

        Args:
            path: File path

        Returns:
            True if file extension is in allowed list
        """
        return path.suffix.lower() in self.config.allowed_extensions
