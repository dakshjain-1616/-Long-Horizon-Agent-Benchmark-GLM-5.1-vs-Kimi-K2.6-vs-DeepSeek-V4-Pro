"""File edit tool for reading and editing files."""

import os
from typing import Any

from .base import BaseTool, ToolResult


class FileEditTool(BaseTool):
    """Tool for reading and editing files."""

    def __init__(self, mock_mode: bool = False) -> None:
        super().__init__(
            name="file_edit",
            description="Read, write, or edit files on the filesystem",
            mock_mode=mock_mode,
        )

    async def execute(
        self,
        operation: str,
        path: str,
        content: str | None = None,
        old_string: str | None = None,
        new_string: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> ToolResult:
        """Execute file operation.

        Args:
            operation: One of 'read', 'write', 'edit', 'delete'
            path: File path
            content: Content for write operation
            old_string: String to replace for edit operation
            new_string: Replacement string for edit operation
            offset: Line offset for read operation
            limit: Max lines to read
        """
        if self.mock_mode:
            return self._mock_execute(operation, path, content, old_string, new_string)

        try:
            if operation == "read":
                return self._read_file(path, offset, limit)
            elif operation == "write":
                return self._write_file(path, content)
            elif operation == "edit":
                return self._edit_file(path, old_string, new_string)
            elif operation == "delete":
                return self._delete_file(path)
            else:
                return ToolResult(success=False, output="", error=f"Unknown operation: {operation}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _read_file(self, path: str, offset: int, limit: int) -> ToolResult:
        """Read file contents."""
        if not os.path.exists(path):
            return ToolResult(success=False, output="", error=f"File not found: {path}")

        with open(path) as f:
            lines = f.readlines()

        start = offset
        end = min(offset + limit, len(lines))
        selected_lines = lines[start:end]

        output = "".join(selected_lines)
        metadata = {"total_lines": len(lines), "shown_lines": len(selected_lines), "offset": offset}

        return ToolResult(success=True, output=output, metadata=metadata)

    def _write_file(self, path: str, content: str | None) -> ToolResult:
        """Write content to file."""
        if content is None:
            return ToolResult(success=False, output="", error="Content required for write operation")

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        return ToolResult(success=True, output=f"File written: {path}", metadata={"path": path, "size": len(content)})

    def _edit_file(self, path: str, old_string: str | None, new_string: str | None) -> ToolResult:
        """Edit file by replacing string."""
        if old_string is None or new_string is None:
            return ToolResult(success=False, output="", error="old_string and new_string required for edit")

        if not os.path.exists(path):
            return ToolResult(success=False, output="", error=f"File not found: {path}")

        with open(path) as f:
            content = f.read()

        if old_string not in content:
            return ToolResult(success=False, output="", error=f"old_string not found in file: {old_string[:50]}...")

        new_content = content.replace(old_string, new_string, 1)

        with open(path, "w") as f:
            f.write(new_content)

        return ToolResult(success=True, output=f"File edited: {path}", metadata={"path": path, "replacements": 1})

    def _delete_file(self, path: str) -> ToolResult:
        """Delete a file."""
        if not os.path.exists(path):
            return ToolResult(success=False, output="", error=f"File not found: {path}")

        os.remove(path)
        return ToolResult(success=True, output=f"File deleted: {path}")

    def _mock_execute(
        self,
        operation: str,
        path: str,
        content: str | None,
        old_string: str | None,
        new_string: str | None,
    ) -> ToolResult:
        """Mock execution for testing."""
        return ToolResult(
            success=True,
            output=f"[MOCK] {operation} operation on {path}",
            metadata={"mock": True, "operation": operation, "path": path},
        )

    def _get_parameters_schema(self) -> dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "edit", "delete"],
                    "description": "Operation to perform",
                },
                "path": {
                    "type": "string",
                    "description": "File path",
                },
                "content": {
                    "type": "string",
                    "description": "Content for write operation",
                },
                "old_string": {
                    "type": "string",
                    "description": "String to replace for edit operation",
                },
                "new_string": {
                    "type": "string",
                    "description": "Replacement string for edit operation",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line offset for read operation",
                    "default": 0,
                },
                "limit": {
                    "type": "integer",
                    "description": "Max lines to read",
                    "default": 100,
                },
            },
            "required": ["operation", "path"],
        }
