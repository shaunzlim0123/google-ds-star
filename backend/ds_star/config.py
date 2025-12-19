"""Configuration for DS-STAR."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DSStarConfig:
    """Configuration for DS-STAR session."""

    # Iteration limits
    max_iterations: int = 20
    max_debug_attempts: int = 3

    # Code execution
    execution_timeout_seconds: float = 60.0
    max_output_length: int = 10000

    # LLM settings
    # Note: gpt-5-nano only supports temperature=1.0 (not configurable)
    # This setting is kept for potential future compatibility with other models
    temperature: float = 1.0
    max_tokens: int = 4096

    # Retriever settings (for large datasets)
    use_retriever: bool = False
    retriever_top_k: int = 100

    # Logging
    log_level: str = "INFO"
    log_prompts: bool = False
    log_responses: bool = False

    # Output formatting
    output_format: str | None = None  # e.g., "round to 2 decimal places"

    # Allowed file extensions for analysis
    allowed_extensions: list[str] = field(
        default_factory=lambda: [
            ".csv",
            ".json",
            ".xlsx",
            ".xls",
            ".parquet",
            ".md",
            ".txt",
            ".xml",
            ".yaml",
            ".yml",
        ]
    )


@dataclass
class ExecutorConfig:
    """Configuration for code executor."""

    timeout_seconds: float = 60.0
    max_memory_mb: int = 1024
    max_output_length: int = 10000
    working_directory: str | None = None

    # Safety settings
    allow_network: bool = False
    allow_file_write: bool = True
    blocked_imports: list[str] = field(
        default_factory=lambda: [
            "subprocess",
            "os.system",
            "shutil.rmtree",
            "socket",
            "requests",
            "urllib",
            "http.client",
        ]
    )
