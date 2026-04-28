"""Command-line interface for long-horizon benchmark."""

import asyncio
import json
import os
from pathlib import Path

# Load .env so the documented `cp .env.example .env` flow works without a sourcing step.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .metrics import BenchmarkResult, TaskMetrics
from .judge import judge_output
from .models import DeepSeekClient, GLMClient, KimiClient, MockModelClient, OpusClient
from .plots import generate_all_plots
from .runner import AgentRunner
from .tasks import TASKS
from .tools import CodeSearchTool, FileEditTool, ShellExecTool, WebSearchTool

console = Console()


_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Map our short model ids to (direct base URL, OpenRouter model id, direct env var).
_MODEL_REGISTRY: dict[str, tuple[str, str, str]] = {
    "opus-4.7": (
        "https://openrouter.ai/api/v1",
        "anthropic/claude-opus-4-7",  # verified live on OpenRouter, April 2026: $5/M in, $25/M out
        "ANTHROPIC_API_KEY",
    ),
    "kimi-k2.6": (
        "https://api.moonshot.cn/v1",
        "moonshotai/kimi-k2.6",  # verified live on OpenRouter
        "KIMI_API_KEY",
    ),
    "deepseek-v4-pro": (
        "https://api.deepseek.com/v1",
        "deepseek/deepseek-v4-pro",  # verified live on OpenRouter
        "DEEPSEEK_API_KEY",
    ),
}


def _build_model_config(model_name: str, api_key: str | None) -> "ModelConfig":
    """Build a :class:`ModelConfig` for ``model_name``, preferring OpenRouter.

    If ``OPENROUTER_API_KEY`` is set (and the caller didn't pass an explicit
    ``api_key``), the client points at OpenRouter using the namespaced model id;
    otherwise it falls back to the provider-specific env var and direct endpoint.
    """
    from .models.base import ModelConfig

    if model_name not in _MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_name}")
    direct_base, openrouter_id, direct_env = _MODEL_REGISTRY[model_name]

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        # Caller passed a key — assume direct API.
        return ModelConfig(api_key=api_key, base_url=direct_base, model=model_name)
    if openrouter_key:
        return ModelConfig(api_key=openrouter_key, base_url=_OPENROUTER_BASE_URL, model=openrouter_id)
    direct_key = os.getenv(direct_env, "")
    if not direct_key:
        raise ValueError(
            f"No API key found. Set OPENROUTER_API_KEY (recommended) or {direct_env}, "
            "or pass --api-key explicitly."
        )
    return ModelConfig(api_key=direct_key, base_url=direct_base, model=model_name)


def get_model_client(model_name: str, api_key: str | None = None, mock_mode: bool = False):
    """Return a model client for ``model_name``.

    - ``mock_mode=True`` always returns the :class:`MockModelClient` (no network).
    - Otherwise, resolves the API key and base URL via OpenRouter (preferred)
      with a fallback to the provider-specific direct API.
    """
    if mock_mode:
        return MockModelClient()

    config = _build_model_config(model_name, api_key)

    if model_name == "opus-4.7":
        return OpusClient(config)
    if model_name == "kimi-k2.6":
        return KimiClient(config)
    if model_name == "deepseek-v4-pro":
        return DeepSeekClient(config)
    raise ValueError(f"Unknown model: {model_name}")


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Long-horizon agent benchmark CLI."""
    pass


@cli.command()
@click.option("--model", "-m", required=True, help="Model to use (opus-4.7, kimi-k2.6, deepseek-v4-pro)")
@click.option("--task", "-t", required=True, help="Task ID to run")
@click.option("--mock", is_flag=True, help="Run in mock mode")
@click.option("--output", "-o", type=click.Path(), help="Output file for trace")
@click.option("--max-steps", default=50, help="Maximum steps to run")
@click.option("--judge", "judge_model", default=None, help="LLM judge model id (e.g. openai/gpt-5.5).")
def run(model: str, task: str, mock: bool, output: str | None, max_steps: int, judge_model: str | None):
    """Run a single task."""
    if task not in TASKS:
        console.print(f"[red]Error: Unknown task '{task}'[/red]")
        console.print(f"Available tasks: {', '.join(TASKS.keys())}")
        return

    task_def = TASKS[task]

    async def _run():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_progress = progress.add_task(f"Running {task}...", total=None)

            client = get_model_client(model, mock_mode=mock)
            tools = [
                FileEditTool(mock_mode=mock),
                WebSearchTool(mock_mode=mock),
                ShellExecTool(mock_mode=mock),
                CodeSearchTool(mock_mode=mock),
            ]

            runner = AgentRunner(
                model_client=client,
                tools=[t for t in tools if t.name in task_def.tools],
                max_steps=max_steps,
                mock_mode=mock,
            )

            trace = await runner.run(
                task_id=task,
                prompt=task_def.prompt,
            )

            progress.update(task_progress, completed=True)

            console.print(f"\n[green]Task completed: {trace.success}[/green]")
            console.print(f"Agent tokens: {trace.total_tokens}")
            console.print(f"Agent cost: ${trace.total_cost:.4f}")
            console.print(f"Steps: {len(trace.steps)}")

            judge_result = None
            if judge_model and not mock:
                console.print(f"\n[cyan]Judging with {judge_model}...[/cyan]")
                judge_result = await judge_output(
                    task_prompt=task_def.prompt,
                    agent_output=trace.final_output or "",
                    judge_model=judge_model,
                )
                console.print(f"Judge score: {judge_result.score:.2f}")
                console.print(f"Judge rationale: {judge_result.rationale}")
                console.print(
                    f"Judge tokens: {judge_result.prompt_tokens} in / {judge_result.completion_tokens} out"
                )
                console.print(f"Judge cost: ${judge_result.cost_usd:.4f}")
                console.print(
                    f"\n[bold]Total cost (agent + judge): "
                    f"${trace.total_cost + judge_result.cost_usd:.4f}[/bold]"
                )

            if output:
                payload = trace.to_dict()
                if judge_result:
                    payload["judge"] = {
                        "model": judge_result.model,
                        "score": judge_result.score,
                        "rationale": judge_result.rationale,
                        "prompt_tokens": judge_result.prompt_tokens,
                        "completion_tokens": judge_result.completion_tokens,
                        "cost_usd": judge_result.cost_usd,
                    }
                Path(output).write_text(json.dumps(payload, indent=2))
                console.print(f"Trace saved to: {output}")

            return trace

    asyncio.run(_run())


@cli.command()
@click.option("--model", "-m", required=True, help="Model to use")
@click.option("--category", "-c", help="Filter by category")
@click.option("--mock", is_flag=True, help="Run in mock mode")
@click.option("--output", "-o", type=click.Path(), help="Output directory for results")
@click.option("--judge", "judge_model", default=None, help="LLM judge model id (e.g. openai/gpt-5.5).")
@click.option("--concurrency", "-j", default=4, show_default=True, help="Max tasks to run in parallel.")
def benchmark(
    model: str,
    category: str | None,
    mock: bool,
    output: str | None,
    judge_model: str | None,
    concurrency: int,
):
    """Run benchmark on all tasks (in parallel)."""
    tasks_to_run = {k: v for k, v in TASKS.items() if not category or v.category == category}

    if not tasks_to_run:
        console.print(f"[red]No tasks found for category: {category}[/red]")
        return

    console.print(
        f"Running benchmark with {len(tasks_to_run)} tasks "
        f"(concurrency={concurrency})..."
    )

    output_path = Path(output) if output else None
    if output_path:
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "traces").mkdir(parents=True, exist_ok=True)

    async def _benchmark():
        client = get_model_client(model, mock_mode=mock)
        tools = [
            FileEditTool(mock_mode=mock),
            WebSearchTool(mock_mode=mock),
            ShellExecTool(mock_mode=mock),
            CodeSearchTool(mock_mode=mock),
        ]

        result = BenchmarkResult(model_name=model)
        sem = asyncio.Semaphore(max(1, concurrency))

        with Progress(console=console) as progress:
            task_progress = progress.add_task("Running tasks...", total=len(tasks_to_run))

            async def _run_one(task_id: str, task_def) -> TaskMetrics:
                async with sem:
                    runner = AgentRunner(
                        model_client=client,
                        tools=[t for t in tools if t.name in task_def.tools],
                        max_steps=50,
                        mock_mode=mock,
                    )
                    try:
                        trace = await runner.run(task_id=task_id, prompt=task_def.prompt)
                    except Exception as exc:
                        console.print(f"[red]Task {task_id} failed: {exc}[/red]")
                        progress.advance(task_progress)
                        return TaskMetrics(
                            task_id=task_id,
                            model_name=model,
                            success=False,
                            quality_score=0.0,
                            num_tool_calls=0,
                            total_tokens=0,
                            total_cost=0.0,
                            execution_time=0.0,
                            metadata={"error": str(exc)[:500]},
                        )

                    quality_score = (
                        task_def.grade(trace.final_output) if task_def.expected_output else 0.5
                    )
                    judge_meta: dict = {}
                    judge_cost = 0.0
                    if judge_model and not mock:
                        try:
                            jr = await judge_output(
                                task_prompt=task_def.prompt,
                                agent_output=trace.final_output or "",
                                judge_model=judge_model,
                            )
                            quality_score = jr.score
                            judge_cost = jr.cost_usd
                            judge_meta = {
                                "judge_model": jr.model,
                                "judge_score": jr.score,
                                "judge_rationale": jr.rationale,
                                "judge_cost_usd": jr.cost_usd,
                            }
                        except Exception as e:
                            judge_meta = {"judge_error": str(e)}

                    metrics = TaskMetrics(
                        task_id=task_id,
                        model_name=model,
                        success=trace.success,
                        quality_score=quality_score,
                        num_tool_calls=sum(1 for s in trace.steps if s.tool_results),
                        total_tokens=trace.total_tokens,
                        total_cost=trace.total_cost + judge_cost,
                        execution_time=(trace.end_time or 0) - trace.start_time,
                        metadata=judge_meta,
                    )

                    if output_path:
                        trace_payload = trace.to_dict()
                        if judge_meta:
                            trace_payload["judge"] = judge_meta
                        try:
                            (output_path / "traces" / f"{task_id}.json").write_text(
                                json.dumps(trace_payload, indent=2, default=str)
                            )
                        except Exception as e:
                            console.print(f"[yellow]Could not save trace for {task_id}: {e}[/yellow]")

                    progress.update(task_progress, description=f"Done {task_id}")
                    progress.advance(task_progress)
                    return metrics

            coros = [_run_one(tid, tdef) for tid, tdef in tasks_to_run.items()]
            metrics_list = await asyncio.gather(*coros)
            for m in metrics_list:
                result.add_result(m)

        summary = result.get_summary()

        console.print("\n[bold]Benchmark Results:[/bold]")
        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in summary.items():
            table.add_row(key, str(value))

        console.print(table)

        if output_path:
            full_payload = {
                "summary": summary,
                "model_name": model,
                "task_results": [
                    {
                        "task_id": r.task_id,
                        "model_name": r.model_name,
                        "success": r.success,
                        "quality_score": r.quality_score,
                        "num_tool_calls": r.num_tool_calls,
                        "total_tokens": r.total_tokens,
                        "total_cost": r.total_cost,
                        "execution_time": r.execution_time,
                        "metadata": r.metadata,
                    }
                    for r in result.task_results
                ],
            }
            results_filename = f"results_{model}.json"
            with open(output_path / results_filename, "w") as f:
                json.dump(full_payload, f, indent=2, default=str)
            with open(output_path / "results.json", "w") as f:
                json.dump(summary, f, indent=2, default=str)

            generate_all_plots(result, str(output_path))
            console.print(f"\nResults saved to: {output}")

        return result

    asyncio.run(_benchmark())


@cli.command()
def list_tasks():
    """List all available tasks."""
    table = Table(title="Available Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Tools", style="magenta")

    for task_id, task in TASKS.items():
        table.add_row(
            task_id,
            task.name,
            task.category,
            ", ".join(task.tools),
        )

    console.print(table)
    console.print(f"\nTotal: {len(TASKS)} tasks")


@cli.command()
def list_models():
    """List supported models."""
    table = Table(title="Supported Models")
    table.add_column("Model ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Input Price", style="yellow")
    table.add_column("Output Price", style="yellow")

    models = [
        ("opus-4.7", "Claude Opus 4.7", "$5.00/M", "$25.00/M"),
        ("kimi-k2.6", "Kimi K2.6", "$0.7448/M", "$4.655/M"),
        ("deepseek-v4-pro", "DeepSeek V4-Pro", "$0.435/M", "$0.87/M"),
    ]

    for model_id, name, input_p, output_p in models:
        table.add_row(model_id, name, input_p, output_p)

    console.print(table)


def main() -> None:
    """Console-script entry point (referenced by pyproject.toml)."""
    cli()


if __name__ == "__main__":
    cli()
