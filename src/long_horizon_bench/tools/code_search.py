"""Code search tool for searching code in a codebase."""

import os
import re
from typing import Any

from .base import BaseTool, ToolResult


class CodeSearchTool(BaseTool):
    """Tool for searching code in a codebase."""

    def __init__(self, mock_mode: bool = False) -> None:
        super().__init__(
            name="code_search",
            description="Search for code patterns in a codebase",
            mock_mode=mock_mode,
        )

    async def execute(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str | None = None,
        max_results: int = 20,
    ) -> ToolResult:
        """Execute code search.

        Args:
            pattern: Regex pattern to search for
            path: Root path to search in
            file_pattern: Glob pattern for files to search (e.g., "*.py")
            max_results: Maximum number of results
        """
        if self.mock_mode:
            return self._mock_execute(pattern, path, file_pattern, max_results)

        try:
            results = []
            count = 0

            for root, dirs, files in os.walk(path):
                # Skip hidden directories and common non-code dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__", "venv", ".git"]]

                for filename in files:
                    if file_pattern and not self._match_pattern(filename, file_pattern):
                        continue

                    if count >= max_results:
                        break

                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        matches = list(re.finditer(pattern, content, re.MULTILINE))
                        for match in matches:
                            if count >= max_results:
                                break

                            # Get line number
                            line_num = content[:match.start()].count("\n") + 1
                            lines = content.split("\n")
                            line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                            results.append({
                                "file": filepath,
                                "line": line_num,
                                "match": match.group(),
                                "content": line_content.strip(),
                            })
                            count += 1
                    except Exception:
                        continue

                if count >= max_results:
                    break

            output = f"Found {len(results)} matches for pattern: {pattern}\n\n"
            for r in results:
                output += f"{r['file']}:{r['line']}: {r['content']}\n"

            return ToolResult(
                success=True,
                output=output,
                metadata={"pattern": pattern, "results_count": len(results), "results": results},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def _mock_execute(
        self,
        pattern: str,
        path: str,
        file_pattern: str | None,
        max_results: int,
    ) -> ToolResult:
        """Mock search results."""
        mock_results = [
            {"file": f"{path}/example.py", "line": i + 1, "match": pattern, "content": f"def example_{i}(): pass"}
            for i in range(min(3, max_results))
        ]

        output = f"[MOCK] Found {len(mock_results)} matches for pattern: {pattern}\n\n"
        for r in mock_results:
            output += f"{r['file']}:{r['line']}: {r['content']}\n"

        return ToolResult(
            success=True,
            output=output,
            metadata={"mock": True, "pattern": pattern, "results": mock_results},
        )

    def _get_parameters_schema(self) -> dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Root path to search in",
                    "default": ".",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (e.g., '*.py')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 20,
                },
            },
            "required": ["pattern"],
        }
