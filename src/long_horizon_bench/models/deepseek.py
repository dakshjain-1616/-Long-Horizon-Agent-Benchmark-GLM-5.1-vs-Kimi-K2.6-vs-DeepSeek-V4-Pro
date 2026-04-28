"""DeepSeek V4-Pro model client implementation."""

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import asyncio
import random

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .base import BaseModelClient, ChatResponse, Message, ModelConfig, Usage


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TransportError, httpx.TimeoutException)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or 500 <= code < 600
    return False


class DeepSeekClient(BaseModelClient):
    """Client for DeepSeek V4-Pro."""

    # Verified on OpenRouter (DeepSeek upstream), April 2026: V4-Pro = $0.435/M in, $0.87/M out.
    INPUT_PRICE_PER_1K = 0.000435
    OUTPUT_PRICE_PER_1K = 0.00087

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=config.base_url or "https://api.deepseek.com/v1",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=config.timeout_seconds,
        )

    @retry(
        stop=stop_after_attempt(6),
        wait=wait_exponential(multiplier=2, min=5, max=60),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    async def chat(self, messages: list[Message], tools: list[dict[str, Any]] | None = None, tool_choice: str | None = None) -> ChatResponse:
        start_time = time.time()
        ds_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": self.config.model or "deepseek-v4-pro",
            "messages": ds_messages,
            "temperature": self.config.temperature,
        }
        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        response = await self.client.post("/chat/completions", json=payload)
        if response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    await asyncio.sleep(float(retry_after) + random.uniform(0, 1))
                except ValueError:
                    pass
        response.raise_for_status()
        data = response.json()
        latency_ms = (time.time() - start_time) * 1000
        choice = data["choices"][0]
        message_data = choice["message"]
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        cost = self.estimate_cost(usage.prompt_tokens, usage.completion_tokens)
        self._update_stats(usage, cost)
        tool_calls = None
        if "tool_calls" in message_data:
            tool_calls = [
                {"id": tc["id"], "type": tc["type"], "function": {"name": tc["function"]["name"], "arguments": tc["function"]["arguments"]}}
                for tc in message_data["tool_calls"]
            ]
        return ChatResponse(
            message=Message(role=message_data.get("role", "assistant"), content=message_data.get("content"), tool_calls=tool_calls),
            usage=usage,
            model=data.get("model", self.config.model),
            finish_reason=choice.get("finish_reason"),
            latency_ms=latency_ms,
            cost_usd=cost,
        )

    async def chat_stream(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> AsyncIterator[str]:
        ds_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": self.config.model or "deepseek-v4-pro",
            "messages": ds_messages,
            "temperature": self.config.temperature,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta and delta["content"]:
                            yield delta["content"]
                    except (json.JSONDecodeError, KeyError):
                        continue

    def count_tokens(self, messages: list[Message], tools: list[dict[str, Any]] | None = None) -> int:
        total = 0
        for msg in messages:
            total += 4
            if msg.content:
                total += len(msg.content) // 3
            if msg.tool_calls:
                total += 20 * len(msg.tool_calls)
            if msg.tool_call_id:
                total += 10
        if tools:
            for tool in tools:
                total += len(json.dumps(tool)) // 4
        return max(total, 1)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = (prompt_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (completion_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            msg_dict: dict[str, Any] = {"role": msg.role}
            if msg.content:
                msg_dict["content"] = msg.content
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            if msg.name:
                msg_dict["name"] = msg.name
            result.append(msg_dict)
        return result

    async def close(self) -> None:
        await self.client.aclose()
