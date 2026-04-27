"""Dataset generation and export utilities."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .metrics import BenchmarkResult
from .runner import AgentTrace


def trace_to_dataframe(traces: list[AgentTrace]) -> pd.DataFrame:
    """Convert traces to a pandas DataFrame."""
    rows = []
    for trace in traces:
        for step in trace.steps:
            row = {
                "trace_id": f"{trace.task_id}_{trace.model_name}",
                "task_id": trace.task_id,
                "model_name": trace.model_name,
                "step_number": step.step_number,
                "role": step.role,
                "content": step.content,
                "timestamp": step.timestamp,
                "has_tool_calls": step.tool_calls is not None and len(step.tool_calls) > 0,
                "num_tool_results": len(step.tool_results) if step.tool_results else 0,
                "total_tokens": trace.total_tokens,
                "total_cost": trace.total_cost,
                "success": trace.success,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def export_traces_to_parquet(
    traces: list[AgentTrace],
    output_path: str,
) -> str:
    """Export traces to Parquet format."""
    df = trace_to_dataframe(traces)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Write to parquet
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path)

    return output_path


def export_benchmark_to_parquet(
    result: BenchmarkResult,
    output_path: str,
) -> str:
    """Export benchmark results to Parquet format."""
    data = []
    for r in result.task_results:
        data.append({
            "task_id": r.task_id,
            "model_name": r.model_name,
            "success": r.success,
            "quality_score": r.quality_score,
            "num_tool_calls": r.num_tool_calls,
            "total_tokens": r.total_tokens,
            "total_cost": r.total_cost,
            "execution_time": r.execution_time,
        })

    df = pd.DataFrame(data)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path)

    return output_path


def generate_dataset_card(
    traces: list[AgentTrace],
    output_path: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Generate a dataset card markdown file."""

    # Calculate statistics
    total_steps = sum(len(t.steps) for t in traces)
    total_tool_calls = sum(
        sum(1 for s in t.steps if s.tool_results)
        for t in traces
    )

    successful_traces = sum(1 for t in traces if t.success)

    card = f"""# Long-Horizon Agent Benchmark Dataset

## Overview

This dataset contains agent execution traces from the Long-Horizon Agent Benchmark.

## Dataset Statistics

- **Total Traces**: {len(traces)}
- **Successful Traces**: {successful_traces} ({100*successful_traces/max(len(traces),1):.1f}%)
- **Total Steps**: {total_steps}
- **Total Tool Calls**: {total_tool_calls}
- **Generated**: {datetime.now().isoformat()}

## Models

"""

    # List unique models
    models = {t.model_name for t in traces}
    for model in sorted(models):
        model_traces = [t for t in traces if t.model_name == model]
        card += f"- **{model}**: {len(model_traces)} traces\n"

    card += "\n## Tasks\n\n"

    # List tasks
    tasks = {t.task_id for t in traces}
    for task in sorted(tasks):
        task_traces = [t for t in traces if t.task_id == task]
        card += f"- **{task}**: {len(task_traces)} traces\n"

    card += """
## Files

- `traces.parquet`: Agent execution traces
- `dataset_card.md`: This file
- `metadata.json`: Additional metadata

## Schema

### traces.parquet

| Column | Type | Description |
|--------|------|-------------|
| trace_id | string | Unique trace identifier |
| task_id | string | Task identifier |
| model_name | string | Model used |
| step_number | int | Step number in trace |
| role | string | Message role (user/assistant/tool) |
| content | string | Message content |
| timestamp | datetime | Step timestamp |
| has_tool_calls | bool | Whether step had tool calls |
| num_tool_results | int | Number of tool results |
| total_tokens | int | Total tokens in trace |
| total_cost | float | Total cost in USD |
| success | bool | Whether trace completed successfully |

## Usage

```python
import pandas as pd

# Load traces
df = pd.read_parquet("traces.parquet")

# Filter by model
model_traces = df[df["model_name"] == "mock-model"]

# Filter by task
task_traces = df[df["task_id"] == "refactor_function"]
```

## License

This dataset is provided for research and evaluation purposes.
"""

    if metadata:
        card += f"\n## Additional Metadata\n\n```json\n{json.dumps(metadata, indent=2)}\n```\n"

    Path(output_path).write_text(card)
    return output_path


def export_dataset(
    traces: list[AgentTrace],
    output_dir: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Export complete dataset with all formats."""
    os.makedirs(output_dir, exist_ok=True)

    # Export traces to parquet
    parquet_path = os.path.join(output_dir, "traces.parquet")
    export_traces_to_parquet(traces, parquet_path)

    # Generate dataset card
    card_path = os.path.join(output_dir, "dataset_card.md")
    generate_dataset_card(traces, card_path, metadata)

    # Export metadata
    meta_path = os.path.join(output_dir, "metadata.json")
    meta = {
        "version": "0.1.0",
        "generated_at": datetime.now().isoformat(),
        "num_traces": len(traces),
        "models": list({t.model_name for t in traces}),
        "tasks": list({t.task_id for t in traces}),
    }
    if metadata:
        meta.update(metadata)
    Path(meta_path).write_text(json.dumps(meta, indent=2))

    return {
        "parquet": parquet_path,
        "card": card_path,
        "metadata": meta_path,
    }


def load_traces_from_parquet(parquet_path: str) -> list[AgentTrace]:
    """Load traces from Parquet file."""
    df = pd.read_parquet(parquet_path)

    # Group by trace_id to reconstruct traces
    traces = []
    for trace_id in df["trace_id"].unique():
        trace_df = df[df["trace_id"] == trace_id]

        # Get trace-level info from first row
        first_row = trace_df.iloc[0]
        trace = AgentTrace(
            task_id=first_row["task_id"],
            model_name=first_row["model_name"],
            start_time=first_row["timestamp"].timestamp() if hasattr(first_row["timestamp"], "timestamp") else 0,
            total_tokens=first_row["total_tokens"],
            total_cost=first_row["total_cost"],
            success=first_row["success"],
        )
        traces.append(trace)

    return traces
