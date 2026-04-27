"""Shell execution tool for running commands."""

import subprocess
from typing import Any

from .base import BaseTool, ToolResult


class ShellExecTool(BaseTool):
    """Tool for executing shell commands."""

    def __init__(self, mock_mode: bool = False, allowed_commands: list | None = None) -> None:
        super().__init__(
            name="shell_exec",
            description="Execute shell commands",
            mock_mode=mock_mode,
        )
        self.allowed_commands = allowed_commands or ["ls", "cat", "grep", "find", "pwd", "echo"]

    async def execute(  # type: ignore[override]
        self, command: str, timeout: int = 30, cwd: str | None = None) -> ToolResult:
        """Execute shell command.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds
            cwd: Working directory for command
        """
        if self.mock_mode:
            return self._mock_execute(command, cwd)

        # Security check
        cmd_parts = command.split()
        if cmd_parts and cmd_parts[0] not in self.allowed_commands:
            return ToolResult(
                success=False,
                output="",
                error=f"Command '{cmd_parts[0]}' not in allowed commands list",
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"

            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else None,
                metadata={
                    "returncode": result.returncode,
                    "command": command,
                    "cwd": cwd,
                },
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output="", error=f"Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _mock_execute(self, command: str, cwd: str | None) -> ToolResult:
        """Mock execution."""
        return ToolResult(
            success=True,
            output=f"[MOCK] Executed: {command}",
            metadata={"mock": True, "command": command, "cwd": cwd},
        )

    def _get_parameters_schema(self) -> dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Command timeout in seconds",
                    "default": 30,
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for command",
                },
            },
            "required": ["command"],
        }
