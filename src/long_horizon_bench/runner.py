"""Agent runner with tool dispatch and tracing."""

import json
import time
from dataclasses import dataclass, field
from typing import Any

from .models.base import BaseModelClient, Message
from .tools.base import BaseTool, ToolResult


@dataclass
class TraceStep:
    """A single step in the agent trace."""
    step_number: int
    timestamp: float
    role: str  # "user", "assistant", "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_results: list[ToolResult] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTrace:
    """Complete trace of an agent run."""
    task_id: str
    model_name: str
    start_time: float
    end_time: float | None = None
    steps: list[TraceStep] = field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    success: bool = False
    final_output: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "task_id": self.task_id,
            "model_name": self.model_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "success": self.success,
            "final_output": self.final_output,
            "steps": [
                {
                    "step_number": s.step_number,
                    "timestamp": s.timestamp,
                    "role": s.role,
                    "content": s.content,
                    "tool_calls": s.tool_calls,
                    "tool_results": [
                        {
                            "success": r.success,
                            "output": r.output,
                            "error": r.error,
                            "metadata": r.metadata,
                        }
                        for r in (s.tool_results or [])
                    ],
                    "metadata": s.metadata,
                }
                for s in self.steps
            ],
            "metadata": self.metadata,
        }


class AgentRunner:
    """Agent runner that orchestrates model and tools."""

    def __init__(
        self,
        model_client: BaseModelClient,
        tools: list[BaseTool],
        max_steps: int = 50,
        mock_mode: bool = False,
    ) -> None:
        self.model_client = model_client
        self.tools = {tool.name: tool for tool in tools}
        self.max_steps = max_steps
        self.mock_mode = mock_mode
        self.tool_schemas = [tool.get_schema() for tool in tools]

    async def run(
        self,
        task_id: str,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AgentTrace:
        """Run the agent on a task."""
        trace = AgentTrace(
            task_id=task_id,
            model_name=self.model_client.config.model,
            start_time=time.time(),
        )

        messages: list[Message] = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))

        trace.steps.append(TraceStep(
            step_number=0,
            timestamp=time.time(),
            role="user",
            content=prompt,
        ))

        for step in range(1, self.max_steps + 1):
            response = await self.model_client.chat(
                messages=messages,
                tools=self.tool_schemas if self.tools else None,
            )

            trace.total_tokens += response.usage.total_tokens
            trace.total_cost += self.model_client.estimate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )

            assistant_message = Message(
                role="assistant",
                content=response.message.content or "",
                tool_calls=response.message.tool_calls,
            )
            messages.append(assistant_message)

            step_data = TraceStep(
                step_number=step,
                timestamp=time.time(),
                role="assistant",
                content=response.message.content or "",
                tool_calls=response.message.tool_calls,
            )

            if not response.message.tool_calls:
                trace.steps.append(step_data)
                trace.success = True
                trace.final_output = response.message.content or ""
                break

            tool_results = await self._execute_tool_calls(response.message.tool_calls)
            step_data.tool_results = tool_results
            trace.steps.append(step_data)

            for result in tool_results:
                tool_message = Message(
                    role="tool",
                    content=result.output if result.success else result.error,
                )
                messages.append(tool_message)

        trace.end_time = time.time()
        return trace

    async def _execute_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """Execute tool calls from model response."""
        results = []
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name", "")
            arguments = json.loads(call.get("function", {}).get("arguments", "{}"))

            if tool_name in self.tools:
                try:
                    result = await self.tools[tool_name].execute(**arguments)
                except Exception as e:
                    result = ToolResult(
                        success=False,
                        output="",
                        error=f"Tool execution error: {str(e)}",
                    )
            else:
                result = ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown tool: {tool_name}",
                )
            results.append(result)
        return results

    def get_stats(self) -> dict[str, Any]:
        """Get runner statistics."""
        return {
            "model_name": self.model_client.config.model,
            "max_steps": self.max_steps,
            "available_tools": list(self.tools.keys()),
            "mock_mode": self.mock_mode,
        }
