"""Logging utilities for DS-STAR."""

from __future__ import annotations

import logging
import sys
from typing import TextIO


def setup_logger(
    name: str = "ds_star",
    level: str = "INFO",
    stream: TextIO | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """Set up a logger with consistent formatting.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        stream: Output stream (defaults to stderr)
        format_string: Custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


class AgentLogger:
    """Specialized logger for agent operations."""

    def __init__(self, agent_name: str, base_logger: logging.Logger | None = None):
        """Initialize agent logger.

        Args:
            agent_name: Name of the agent
            base_logger: Base logger to use (creates one if not provided)
        """
        self.agent_name = agent_name
        self.logger = base_logger or setup_logger(f"ds_star.{agent_name}")

    def start(self, context: str = "") -> None:
        """Log agent start."""
        msg = f"[{self.agent_name}] Starting"
        if context:
            msg += f": {context}"
        self.logger.info(msg)

    def complete(self, result_summary: str = "") -> None:
        """Log agent completion."""
        msg = f"[{self.agent_name}] Completed"
        if result_summary:
            msg += f": {result_summary}"
        self.logger.info(msg)

    def error(self, error: str) -> None:
        """Log agent error."""
        self.logger.error(f"[{self.agent_name}] Error: {error}")

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(f"[{self.agent_name}] {message}")

    def prompt(self, prompt_preview: str) -> None:
        """Log prompt (truncated)."""
        preview = prompt_preview[:500] + "..." if len(prompt_preview) > 500 else prompt_preview
        self.logger.debug(f"[{self.agent_name}] Prompt: {preview}")

    def response(self, response_preview: str) -> None:
        """Log response (truncated)."""
        preview = response_preview[:500] + "..." if len(response_preview) > 500 else response_preview
        self.logger.debug(f"[{self.agent_name}] Response: {preview}")
