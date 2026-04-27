"""Base tool interface for long-horizon benchmark."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] | None = None


class BaseTool(ABC):
    """Abstract base class for tools."""

    def __init__(self, name: str, description: str, mock_mode: bool = False) -> None:
        self.name = name
        self.description = description
        self.mock_mode = mock_mode

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def get_schema(self) -> dict[str, Any]:
        """Get JSON schema for the tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._get_parameters_schema(),
            },
        }

    @abstractmethod
    def _get_parameters_schema(self) -> dict[str, Any]:
        """Get parameters schema for the tool."""
        pass
