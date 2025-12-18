"""DS-STAR: Data Science Agent via Iterative Planning and Verification.

DS-STAR is a data science agent that transforms raw data into actionable
insights through iterative planning and verification.

Example:
    >>> import asyncio
    >>> from ds_star import DSStarSession, OpenAIProvider, DSStarConfig
    >>>
    >>> async def main():
    ...     provider = OpenAIProvider(api_key="sk-...")
    ...     session = DSStarSession(provider=provider)
    ...     answer = await session.run(
    ...         query="What is the average sales by region?",
    ...         data_files=["./data/sales.csv"]
    ...     )
    ...     print(answer)
    >>>
    >>> asyncio.run(main())
"""

from .config import DSStarConfig, ExecutorConfig
from .core.executor import CodeExecutor
from .core.session import DSStarSession
from .core.types import (
    CodeBlock,
    DSStarState,
    ExecutionResult,
    FileDescription,
    RouterDecision,
    RouterOutput,
    Step,
    StepStatus,
    VerificationResult,
)
from .providers.base import LLMProvider, LLMResponse, Message
from .providers.openai_provider import OpenAIProvider

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "DSStarSession",
    "DSStarConfig",
    "ExecutorConfig",
    "CodeExecutor",
    # Providers
    "LLMProvider",
    "LLMResponse",
    "Message",
    "OpenAIProvider",
    # Types
    "DSStarState",
    "FileDescription",
    "Step",
    "StepStatus",
    "CodeBlock",
    "ExecutionResult",
    "RouterDecision",
    "RouterOutput",
    "VerificationResult",
]
