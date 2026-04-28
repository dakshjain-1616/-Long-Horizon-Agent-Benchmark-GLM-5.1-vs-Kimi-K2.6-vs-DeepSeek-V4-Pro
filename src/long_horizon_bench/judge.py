"""LLM judge that scores task outputs via OpenRouter (default: GPT-5.5)."""

import json
import os
import re
from dataclasses import dataclass

import httpx

# Verified on OpenRouter, April 2026: GPT-5.5 = $5/M in, $30/M out.
GPT55_INPUT_PRICE_PER_1K = 0.005
GPT55_OUTPUT_PRICE_PER_1K = 0.030

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

JUDGE_SYSTEM_PROMPT = """You are an impartial judge scoring an AI agent's response to a task.

Score the response on a 0.0 to 1.0 scale based on:
- Correctness: does it solve the task?
- Completeness: did it address all parts?
- Quality: is the work well-structured and clear?

Respond with ONLY a JSON object, no other text:
{"score": <float 0.0-1.0>, "rationale": "<one or two sentences>"}"""


@dataclass
class JudgeResult:
    score: float
    rationale: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    model: str


async def judge_output(
    task_prompt: str,
    agent_output: str,
    judge_model: str = "openai/gpt-5.5",
    api_key: str | None = None,
) -> JudgeResult:
    """Score ``agent_output`` for ``task_prompt`` using an LLM judge via OpenRouter."""
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY required for LLM judge.")

    user_msg = (
        f"TASK PROMPT:\n{task_prompt}\n\n"
        f"AGENT RESPONSE:\n{agent_output}\n\n"
        "Score it now."
    )

    payload = {
        "model": judge_model,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.0,
    }

    async with httpx.AsyncClient(
        base_url=OPENROUTER_BASE_URL,
        headers={"Authorization": f"Bearer {key}"},
        timeout=120.0,
    ) as client:
        resp = await client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"].get("content") or ""
    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    score, rationale = _parse_judge_response(content)

    cost = (
        (prompt_tokens / 1000) * GPT55_INPUT_PRICE_PER_1K
        + (completion_tokens / 1000) * GPT55_OUTPUT_PRICE_PER_1K
    )

    return JudgeResult(
        score=score,
        rationale=rationale,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=cost,
        model=data.get("model", judge_model),
    )


def _parse_judge_response(content: str) -> tuple[float, str]:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return 0.0, f"Could not parse judge response: {content[:200]}"
    try:
        obj = json.loads(match.group(0))
        score = float(obj.get("score", 0.0))
        score = max(0.0, min(1.0, score))
        rationale = str(obj.get("rationale", ""))
        return score, rationale
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return 0.0, f"Parse error: {e}; raw: {content[:200]}"
