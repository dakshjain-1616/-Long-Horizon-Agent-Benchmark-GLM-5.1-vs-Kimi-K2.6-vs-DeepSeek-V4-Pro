"""Command-line interface for long-horizon benchmark."""

import asyncio
import json
import os
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .metrics import BenchmarkResult, TaskMetrics
from .models import DeepSeekClient, GLMClient, KimiClient, MockModelClient
from .plots import generate_all_plots
from .runner import AgentRunner
from .tasks import TASKS
from .tools import CodeSearchTool, FileEditTool, ShellExecTool, WebSearchTool

console = Console()


_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Map our short model ids to (direct base URL, OpenRouter model id, direct env var).
_MODEL_REGISTRY: dict[str, tuple[str, str, str]] = {
    "glm-5.1": (
        "https://open.bigmodel.cn/api/paas/v4",
        "z-ai/glm-5.1",  # verified live on OpenRouter (Z.ai is the upstream provider id)
        "GLM_API_KEY",
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

    if model_name == "glm-5.1":
        return GLMClient(config)
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
@click.option("--model", "-m", required=True, help="Model to use (glm-5.1, kimi-k2.6, deepseek-v4-pro)")
@click.option("--task", "-t", required=True, help="Task ID to run")
@click.option("--mock", is_flag=True, help="Run in mock mode")
@click.option("--output", "-o", type=click.Path(), help="Output file for trace")
@click.option("--max-steps", default=50, help="Maximum steps to run")
def run(model: str, task: str, mock: bool, output: str | None, max_steps: int):
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
            console.print(f"Total tokens: {trace.total_tokens}")
            console.print(f"Total cost: ${trace.total_cost:.4f}")
            console.print(f"Steps: {len(trace.steps)}")

            if output:
                Path(output).write_text(json.dumps(trace.to_dict(), indent=2))
                console.print(f"Trace saved to: {output}")

            return trace

    asyncio.run(_run())


@cli.command()
@click.option("--model", "-m", required=True, help="Model to use")
@click.option("--category", "-c", help="Filter by category")
@click.option("--mock", is_flag=True, help="Run in mock mode")
@click.option("--output", "-o", type=click.Path(), help="Output directory for results")
def benchmark(model: str, category: str | None, mock: bool, output: str | None):
    """Run benchmark on all tasks."""
    tasks_to_run = {k: v for k, v in TASKS.items() if not category or v.category == category}

    if not tasks_to_run:
        console.print(f"[red]No tasks found for category: {category}[/red]")
        return

    console.print(f"Running benchmark with {len(tasks_to_run)} tasks...")

    async def _benchmark():
        client = get_model_client(model, mock_mode=mock)
        tools = [
            FileEditTool(mock_mode=mock),
            WebSearchTool(mock_mode=mock),
            ShellExecTool(mock_mode=mock),
            CodeSearchTool(mock_mode=mock),
        ]

        result = BenchmarkResult(model_name=model)

        with Progress(console=console) as progress:
            task_progress = progress.add_task("Running tasks...", total=len(tasks_to_run))

            for task_id, task_def in tasks_to_run.items():
                progress.update(task_progress, description=f"Running {task_id}...")

                runner = AgentRunner(
                    model_client=client,
                    tools=[t for t in tools if t.name in task_def.tools],
                    max_steps=50,
                    mock_mode=mock,
                )

                trace = await runner.run(
                    task_id=task_id,
                    prompt=task_def.prompt,
                )

                quality_score = task_def.grade(trace.final_output) if task_def.expected_output else 0.5

                task_metrics = TaskMetrics(
                    task_id=task_id,
                    model_name=model,
                    success=trace.success,
                    quality_score=quality_score,
                    num_tool_calls=sum(1 for s in trace.steps if s.tool_results),
                    total_tokens=trace.total_tokens,
                    total_cost=trace.total_cost,
                    execution_time=(trace.end_time or 0) - trace.start_time,
                )
                result.add_result(task_metrics)
                progress.advance(task_progress)

        summary = result.get_summary()

        console.print("\n[bold]Benchmark Results:[/bold]")
        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in summary.items():
            table.add_row(key, str(value))

        console.print(table)

        if output:
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)

            with open(output_path / "results.json", "w") as f:
                json.dump(summary, f, indent=2)

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
        ("glm-5.1", "GLM-5.1", "$1.05/M", "$3.50/M"),
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
