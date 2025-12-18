"""Analyzer agent for extracting information from data files."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from ..core.agent import BaseAgent
from ..core.types import DSStarState, FileDescription
from ..prompts.templates import ANALYZER_SYSTEM, ANALYZER_USER
from ..providers.base import LLMProvider, Message


class AnalyzerAgent(BaseAgent[str, FileDescription]):
    """Agent that analyzes data files and extracts metadata."""

    def __init__(
        self,
        provider: LLMProvider,
        logger: logging.Logger | None = None,
        preview_lines: int = 50,
        preview_bytes: int = 5000,
    ):
        """Initialize the analyzer agent.

        Args:
            provider: LLM provider
            logger: Logger instance
            preview_lines: Number of lines to preview
            preview_bytes: Number of bytes to preview
        """
        super().__init__(provider, logger)
        self.preview_lines = preview_lines
        self.preview_bytes = preview_bytes

    @property
    def name(self) -> str:
        return "Analyzer"

    def build_prompt(self, state: DSStarState, file_path: str) -> list[Message]:
        """Build prompt for file analysis.

        Args:
            state: Current session state (not used directly)
            file_path: Path to the file to analyze

        Returns:
            Messages for LLM
        """
        path = Path(file_path)
        file_size = path.stat().st_size if path.exists() else 0
        file_extension = path.suffix.lower()

        # Read file preview
        file_preview = self._get_file_preview(file_path)

        user_prompt = ANALYZER_USER.format(
            file_path=file_path,
            file_extension=file_extension,
            file_size=file_size,
            preview_lines=self.preview_lines,
            preview_bytes=self.preview_bytes,
            file_preview=file_preview,
        )

        return [
            Message(role="system", content=ANALYZER_SYSTEM),
            Message(role="user", content=user_prompt),
        ]

    def parse_response(self, response: str) -> FileDescription:
        """Parse LLM response into FileDescription.

        Args:
            response: Raw LLM response

        Returns:
            FileDescription object
        """
        # Extract JSON from response (may be wrapped in markdown code block)
        json_str = response
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: create basic description from response
            return FileDescription(
                path="",
                file_type="unknown",
                description=response[:500],
            )

        return FileDescription(
            path="",  # Will be set by caller
            file_type=data.get("file_type", "unknown"),
            description=data.get("description", ""),
            schema=data.get("schema"),
            sample_data=data.get("sample_data"),
            row_count=data.get("row_count"),
        )

    def _get_file_preview(self, file_path: str) -> str:
        """Get a preview of the file contents.

        Args:
            file_path: Path to the file

        Returns:
            String preview of file contents
        """
        path = Path(file_path)

        if not path.exists():
            return f"[File not found: {file_path}]"

        try:
            # Handle different file types
            suffix = path.suffix.lower()

            if suffix in [".csv", ".txt", ".md", ".json", ".yaml", ".yml", ".xml"]:
                # Text files - read lines
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    lines = []
                    total_bytes = 0
                    for i, line in enumerate(f):
                        if i >= self.preview_lines or total_bytes >= self.preview_bytes:
                            break
                        lines.append(line.rstrip("\n"))
                        total_bytes += len(line)
                    return "\n".join(lines)

            elif suffix in [".xlsx", ".xls"]:
                # Excel files - use pandas
                try:
                    import pandas as pd

                    df = pd.read_excel(path, nrows=self.preview_lines)
                    return df.to_string()
                except Exception as e:
                    return f"[Error reading Excel file: {e}]"

            elif suffix == ".parquet":
                # Parquet files
                try:
                    import pandas as pd

                    df = pd.read_parquet(path).head(self.preview_lines)
                    return df.to_string()
                except Exception as e:
                    return f"[Error reading Parquet file: {e}]"

            else:
                # Binary or unknown - read first N bytes
                with open(path, "rb") as f:
                    data = f.read(self.preview_bytes)
                    try:
                        return data.decode("utf-8", errors="replace")
                    except Exception:
                        return f"[Binary file, {len(data)} bytes]"

        except Exception as e:
            return f"[Error reading file: {e}]"

    async def analyze_file(self, file_path: str) -> FileDescription:
        """Convenience method to analyze a single file.

        Args:
            file_path: Path to the file

        Returns:
            FileDescription with analysis results
        """
        # Create minimal state for the agent
        state = DSStarState(query="", data_files=[file_path])

        desc = await self.run(state, file_path)
        desc.path = file_path
        desc.size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else None

        return desc
