"""Base model client interface for long-horizon benchmark."""

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    """A chat message."""
    role: str
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class Usage:
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ChatResponse:
    """Response from a chat completion."""
    message: Message
    usage: Usage
    model: str
    finish_reason: str | None = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0


@dataclass
class ModelConfig:
    """Configuration for a model client."""
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float = 60.0
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int | None = None


class BaseModelClient(ABC):
    """Abstract base class for model clients."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._total_calls = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    @abstractmethod
    async def chat(self, messages: list[Message], tools: list[dict[str, Any]] | None = None, tool_choice: str | None = None) -> ChatResponse:
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> AsyncIterator[str]:
        pass

    @abstractmethod
    def count_tokens(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> int:
        pass

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        pass

    def get_stats(self) -> dict[str, int | float]:
        return {"total_calls": self._total_calls, "total_tokens": self._total_tokens, "total_cost_usd": self._total_cost}

    def _update_stats(self, usage: Usage, cost: float) -> None:
        self._total_calls += 1
        self._total_tokens += usage.total_tokens
        self._total_cost += cost


class MockModelClient(BaseModelClient):
    """Mock client for testing without API calls."""

    def __init__(self, config: ModelConfig | None = None) -> None:
        if config is None:
            config = ModelConfig(api_key="mock", base_url="mock", model="mock-model")
        super().__init__(config)
        self._response_counter = 0

    async def chat(self, messages: list[Message], tools: list[dict[str, Any]] | None = None, tool_choice: str | None = None) -> ChatResponse:
        start_time = time.time()
        self._response_counter += 1
        messages[-1].content if messages else ""
        if tools and self._response_counter % 3 == 0:
            tool = tools[0]
            content = None
            tool_calls = [{"id": f"call_{self._response_counter}", "type": "function", "function": {"name": tool["function"]["name"], "arguments": '{"query": "example"}'}}]
        else:
            content = f"Mock response #{self._response_counter}"
            tool_calls = None
        prompt_tokens = self.count_tokens(messages, tools)
        completion_tokens = 20
        usage = Usage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)
        cost = self.estimate_cost(prompt_tokens, completion_tokens)
        self._update_stats(usage, cost)
        latency_ms = (time.time() - start_time) * 1000
        return ChatResponse(message=Message(role="assistant", content=content, tool_calls=tool_calls), usage=usage, model=self.config.model, finish_reason="stop", latency_ms=latency_ms, cost_usd=cost)

    async def chat_stream(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> AsyncIterator[str]:
        for chunk in ["Mock ", "response ", f"#{self._response_counter}"]:
            yield chunk

    def count_tokens(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> int:
        total = 0
        for msg in messages:
            if msg.content:
                total += len(msg.content) // 4
            if msg.tool_calls:
                total += 20 * len(msg.tool_calls)
        if tools:
            total += 50 * len(tools)
        return max(total, 1)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return 0.0
