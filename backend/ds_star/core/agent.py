"""Base agent class for DS-STAR agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..providers.base import LLMProvider, Message
from .types import DSStarState

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Abstract base class for all DS-STAR agents.

    Each agent has a specific role in the DS-STAR pipeline:
    - Analyzer: Extracts information from data files
    - Planner: Generates high-level plan steps
    - Coder: Implements steps as Python code
    - Verifier: Checks if the plan is sufficient
    - Router: Decides to add steps or backtrack
    - Debugger: Fixes failed code
    - Finalizer: Formats the final output
    """

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ):
        """Initialize the agent.

        Args:
            provider: LLM provider for making API calls
            logger: Logger instance (creates one if not provided)
            temperature: Sampling temperature (Note: gpt-5-nano only supports 1.0)
            max_tokens: Maximum tokens in LLM response
        """
        self.provider = provider
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier for logging."""
        ...

    @abstractmethod
    def build_prompt(self, state: DSStarState, input_data: InputT) -> list[Message]:
        """Construct the prompt messages for this agent.

        Args:
            state: Current DS-STAR session state
            input_data: Input specific to this agent's task

        Returns:
            List of messages to send to the LLM
        """
        ...

    @abstractmethod
    def parse_response(self, response: str) -> OutputT:
        """Parse LLM response into structured output.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed output of the appropriate type
        """
        ...

    async def run(self, state: DSStarState, input_data: InputT) -> OutputT:
        """Execute the agent: build prompt, call LLM, parse response.

        Args:
            state: Current DS-STAR session state
            input_data: Input specific to this agent's task

        Returns:
            Parsed output from the agent
        """
        self.logger.info(f"{self.name} starting...")

        messages = self.build_prompt(state, input_data)
        self.logger.debug(f"Prompt messages: {len(messages)}")

        response = await self.provider.complete(
            messages,
            max_tokens=self.max_tokens,
        )
        self.logger.debug(f"Response length: {len(response.content)} chars")

        output = self.parse_response(response.content)
        self.logger.info(f"{self.name} completed.")

        return output
