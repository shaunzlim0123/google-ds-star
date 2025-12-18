"""Base protocol for LLM providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Protocol, runtime_checkable


@dataclass
class Message:
    """A message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM completion."""

    content: str
    model: str
    usage: dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers - enables easy swapping between providers."""

    async def complete(
        self,
        messages: list[Message],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Generate a completion from messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response

        Returns:
            LLMResponse with content and metadata
        """
        ...

    async def complete_stream(
        self,
        messages: list[Message],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            String tokens as they are generated
        """
        ...

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        ...
