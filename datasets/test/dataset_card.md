# Long-Horizon Agent Benchmark Dataset

## Overview

This dataset contains agent execution traces from the Long-Horizon Agent Benchmark.

## Dataset Statistics

- **Total Traces**: 1
- **Successful Traces**: 1 (100.0%)
- **Total Steps**: 2
- **Total Tool Calls**: 0
- **Generated**: 2026-04-27T08:29:53.534645

## Models

- **mock-model**: 1 traces

## Tasks

- **test_task**: 1 traces

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
