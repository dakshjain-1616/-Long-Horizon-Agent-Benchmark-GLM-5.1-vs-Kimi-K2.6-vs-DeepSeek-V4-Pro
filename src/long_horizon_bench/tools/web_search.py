"""Web search tool for searching the internet."""

from typing import Any

from .base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Tool for searching the web."""

    def __init__(self, mock_mode: bool = False, api_key: str | None = None) -> None:
        super().__init__(
            name="web_search",
            description="Search the web for information",
            mock_mode=mock_mode,
        )
        self.api_key = api_key

    async def execute(  # type: ignore[override]
        self, query: str, num_results: int = 5) -> ToolResult:
        """Execute web search."""
        if self.mock_mode:
            return self._mock_execute(query, num_results)
        return ToolResult(
            success=True,
            output=f"Web search for: {query}\n[Real search API not configured]",
            metadata={"query": query, "num_results": num_results},
        )

    def _mock_execute(self, query: str, num_results: int) -> ToolResult:
        """Mock search results."""
        mock_results = [
            {"title": f"Result {i+1} for {query}", "url": f"https://example.com/{i}", "snippet": f"This is a mock result {i+1}"}
            for i in range(num_results)
        ]
        output = f"Search results for: {query}\n\n"
        for i, result in enumerate(mock_results, 1):
            output += f"{i}. {result['title']}\n   {result['url']}\n   {result['snippet']}\n\n"
        return ToolResult(success=True, output=output, metadata={"mock": True, "query": query, "results": mock_results})

    def _get_parameters_schema(self) -> dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results to return", "default": 5},
            },
            "required": ["query"],
        }
