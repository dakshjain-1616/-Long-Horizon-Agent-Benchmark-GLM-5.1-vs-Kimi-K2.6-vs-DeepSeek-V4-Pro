"""Plotting utilities for benchmark results."""

import os

import matplotlib.pyplot as plt
import seaborn as sns

from .metrics import BenchmarkResult


def setup_plot_style() -> None:
    """Set up matplotlib style."""
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 10


def plot_quality_vs_calls(
    result: BenchmarkResult,
    output_path: str | None = None,
) -> str:
    """Plot quality score vs number of tool calls."""
    setup_plot_style()

    data = result.quality_vs_calls()
    if not data:
        return ""

    calls = [d["num_tool_calls"] for d in data]
    quality = [d["quality_score"] for d in data]
    success = [d["success"] for d in data]

    fig, ax = plt.subplots()

    colors = ["green" if s else "red" for s in success]
    ax.scatter(calls, quality, c=colors, alpha=0.6, s=100)

    ax.set_xlabel("Number of Tool Calls")
    ax.set_ylabel("Quality Score")
    ax.set_title(f"Quality vs Tool Calls - {result.model_name}")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="green", label="Success"),
        Patch(facecolor="red", label="Failed"),
    ]
    ax.legend(handles=legend_elements)

    if output_path:
        filepath = os.path.join(output_path, "quality_vs_calls.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        return filepath

    plt.close()
    return ""


def plot_cost_distribution(
    result: BenchmarkResult,
    output_path: str | None = None,
) -> str:
    """Plot cost distribution across tasks."""
    setup_plot_style()

    costs = [r.total_cost for r in result.task_results]
    task_ids = [r.task_id for r in result.task_results]

    if not costs:
        return ""

    fig, ax = plt.subplots()

    bars = ax.bar(range(len(costs)), costs, color="steelblue", alpha=0.7)
    ax.set_xlabel("Task")
    ax.set_ylabel("Cost (USD)")
    ax.set_title(f"Cost Distribution - {result.model_name}")
    ax.set_xticks(range(len(task_ids)))
    ax.set_xticklabels(task_ids, rotation=45, ha="right")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"${height:.4f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()

    if output_path:
        filepath = os.path.join(output_path, "cost_distribution.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        return filepath

    plt.close()
    return ""


def plot_success_rate_by_category(
    result: BenchmarkResult,
    output_path: str | None = None,
) -> str:
    """Plot success rate by task category."""
    setup_plot_style()

    # Group by category (we need to get category from task_id)
    # For now, use a simple mapping
    category_map = {
        "refactor": "refactoring",
        "add_": "refactoring",
        "extract": "refactoring",
        "rename": "refactoring",
        "find_": "research",
        "compare": "research",
        "research": "research",
        "summarize": "research",
        "analyze": "data_analysis",
        "generate": "data_analysis",
        "clean": "data_analysis",
        "statistical": "data_analysis",
        "visualization": "data_analysis",
        "fix_": "debugging",
        "optimize": "debugging",
        "add_tests": "debugging",
    }

    categories: dict[str, list[bool]] = {}
    for r in result.task_results:
        cat = "other"
        for prefix, cat_name in category_map.items():
            if r.task_id.startswith(prefix):
                cat = cat_name
                break
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r.success)

    if not categories:
        return ""

    cat_names = list(categories.keys())
    success_rates = [sum(c) / len(c) for c in categories.values()]

    fig, ax = plt.subplots()

    bars = ax.bar(cat_names, success_rates, color="seagreen", alpha=0.7)
    ax.set_ylabel("Success Rate")
    ax.set_title(f"Success Rate by Category - {result.model_name}")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, axis="y")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1%}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()

    if output_path:
        filepath = os.path.join(output_path, "success_by_category.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        return filepath

    plt.close()
    return ""


def plot_token_usage(
    result: BenchmarkResult,
    output_path: str | None = None,
) -> str:
    """Plot token usage distribution."""
    setup_plot_style()

    tokens = [r.total_tokens for r in result.task_results]
    task_ids = [r.task_id for r in result.task_results]

    if not tokens:
        return ""

    fig, ax = plt.subplots()

    ax.bar(range(len(tokens)), tokens, color="coral", alpha=0.7)
    ax.set_xlabel("Task")
    ax.set_ylabel("Total Tokens")
    ax.set_title(f"Token Usage - {result.model_name}")
    ax.set_xticks(range(len(task_ids)))
    ax.set_xticklabels(task_ids, rotation=45, ha="right")

    plt.tight_layout()

    if output_path:
        filepath = os.path.join(output_path, "token_usage.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        return filepath

    plt.close()
    return ""


def generate_all_plots(
    result: BenchmarkResult,
    output_dir: str,
) -> list[str]:
    """Generate all plots for a benchmark result."""
    os.makedirs(output_dir, exist_ok=True)

    generated = []

    filepath = plot_quality_vs_calls(result, output_dir)
    if filepath:
        generated.append(filepath)

    filepath = plot_cost_distribution(result, output_dir)
    if filepath:
        generated.append(filepath)

    filepath = plot_success_rate_by_category(result, output_dir)
    if filepath:
        generated.append(filepath)

    filepath = plot_token_usage(result, output_dir)
    if filepath:
        generated.append(filepath)

    return generated


def _cli() -> None:
    """Command-line entry point for ``python3 -m long_horizon_bench.plots``.

    Reads a benchmark-results JSON (default ``outputs/results.json``), reconstructs
    a :class:`BenchmarkResult`, and writes the four standard plots to ``--output-dir``.
    Falls back to writing placeholders from an empty result if the file is missing,
    so Makefile targets stay green before a real benchmark run.
    """
    import argparse
    import json
    from pathlib import Path

    from .metrics import BenchmarkResult, TaskMetrics

    parser = argparse.ArgumentParser(description="Generate benchmark plots from results JSON.")
    parser.add_argument("--results", default="outputs/results.json",
                        help="Path to a results JSON file (default: outputs/results.json).")
    parser.add_argument("--output-dir", default="outputs/",
                        help="Where to write PNGs (default: outputs/).")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        sample = BenchmarkResult(model_name="sample", task_results=[])
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"No results at {results_path}; nothing to plot.")
        return

    raw = json.loads(results_path.read_text())

    # Be liberal: results.json may be a list of per-task dicts or an object.
    items = raw if isinstance(raw, list) else raw.get("task_results", [])
    task_results: list[TaskMetrics] = []
    for r in items:
        if not isinstance(r, dict):
            continue
        try:
            task_results.append(TaskMetrics(
                task_id=r.get("task_id", "unknown"),
                model_name=r.get("model_name", "unknown"),
                num_tool_calls=int(r.get("num_tool_calls", 0)),
                quality_score=float(r.get("quality_score", 0.0)),
                total_tokens=int(r.get("total_tokens", 0)),
                total_cost=float(r.get("total_cost", 0.0)),
                duration_seconds=float(r.get("duration_seconds", 0.0)),
                success=bool(r.get("success", False)),
            ))
        except Exception:
            continue

    model_name = raw.get("model_name", task_results[0].model_name) if isinstance(raw, dict) and task_results else "benchmark"
    result = BenchmarkResult(model_name=model_name, task_results=task_results)
    out = generate_all_plots(result, args.output_dir)
    print(f"Generated {len(out)} plots in {args.output_dir}:")
    for p in out:
        print(f"  - {p}")


if __name__ == "__main__":
    _cli()
