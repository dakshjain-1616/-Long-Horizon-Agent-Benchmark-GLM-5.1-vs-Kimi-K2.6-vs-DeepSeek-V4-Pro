"""Re-run a list of failed task_ids sequentially and merge into existing results JSON."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv()

from long_horizon_bench.cli import get_model_client
from long_horizon_bench.metrics import TaskMetrics
from long_horizon_bench.runner import AgentRunner
from long_horizon_bench.tasks import TASKS
from long_horizon_bench.tools import (
    CodeSearchTool,
    FileEditTool,
    ShellExecTool,
    WebSearchTool,
)


async def main(model: str, results_dir: Path, task_ids: list[str]) -> None:
    results_file = results_dir / f"results_{model}.json"
    payload = json.loads(results_file.read_text())

    client = get_model_client(model)
    tools_all = [
        FileEditTool(),
        WebSearchTool(),
        ShellExecTool(),
        CodeSearchTool(),
    ]

    by_id = {r["task_id"]: r for r in payload["task_results"]}

    for task_id in task_ids:
        task_def = TASKS[task_id]
        runner = AgentRunner(
            model_client=client,
            tools=[t for t in tools_all if t.name in task_def.tools],
            max_steps=50,
        )
        print(f"Running {task_id}...", flush=True)
        try:
            trace = await runner.run(task_id=task_id, prompt=task_def.prompt)
        except Exception as exc:
            print(f"  STILL FAILED: {exc}")
            continue

        quality = task_def.grade(trace.final_output) if task_def.expected_output else 0.5
        metrics = TaskMetrics(
            task_id=task_id,
            model_name=model,
            success=trace.success,
            quality_score=quality,
            num_tool_calls=sum(1 for s in trace.steps if s.tool_results),
            total_tokens=trace.total_tokens,
            total_cost=trace.total_cost,
            execution_time=(trace.end_time or 0) - trace.start_time,
            metadata={},
        )
        by_id[task_id] = {
            "task_id": metrics.task_id,
            "model_name": metrics.model_name,
            "success": metrics.success,
            "quality_score": metrics.quality_score,
            "num_tool_calls": metrics.num_tool_calls,
            "total_tokens": metrics.total_tokens,
            "total_cost": metrics.total_cost,
            "execution_time": metrics.execution_time,
            "metadata": metrics.metadata,
        }
        (results_dir / "traces" / f"{task_id}.json").write_text(
            json.dumps(trace.to_dict(), indent=2, default=str)
        )
        print(f"  ok success={metrics.success} q={metrics.quality_score}")

    payload["task_results"] = list(by_id.values())

    rs = payload["task_results"]
    n = len(rs)
    succ = sum(1 for r in rs if r["success"])
    qs = [r["quality_score"] for r in rs]
    payload["summary"]["successful_tasks"] = succ
    payload["summary"]["success_rate"] = succ / n
    payload["summary"]["avg_quality_score"] = sum(qs) / n
    payload["summary"]["min_quality_score"] = min(qs)
    payload["summary"]["max_quality_score"] = max(qs)
    payload["summary"]["total_cost"] = sum(r["total_cost"] for r in rs)
    payload["summary"]["avg_cost"] = payload["summary"]["total_cost"] / n
    payload["summary"]["total_tool_calls"] = sum(r["num_tool_calls"] for r in rs)
    payload["summary"]["avg_tool_calls"] = payload["summary"]["total_tool_calls"] / n

    results_file.write_text(json.dumps(payload, indent=2, default=str))
    (results_dir / "results.json").write_text(
        json.dumps(payload["summary"], indent=2, default=str)
    )
    print(f"\nNew success rate: {succ}/{n} ({succ/n:.0%})")


if __name__ == "__main__":
    asyncio.run(
        main(
            model="deepseek-v4-pro",
            results_dir=Path("results/deepseek"),
            task_ids=["find_best_practices", "clean_data", "statistical_analysis"],
        )
    )
