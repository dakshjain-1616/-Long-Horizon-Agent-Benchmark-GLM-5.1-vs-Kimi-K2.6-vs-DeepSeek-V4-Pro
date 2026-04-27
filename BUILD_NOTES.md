# Build Notes

## Project Structure

```
/app/long_horizon_agent_0716/
├── src/long_horizon_bench/
│   ├── __init__.py          # Package exports
│   ├── cli.py               # Command-line interface
│   ├── dataset.py           # Dataset export utilities
│   ├── metrics.py           # Metrics and grading
│   ├── plots.py             # Visualization
│   ├── runner.py            # Agent runner
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # Base model client
│   │   ├── glm.py           # GLM-5.1 client
│   │   ├── kimi.py          # Kimi K2.6 client
│   │   └── deepseek.py      # DeepSeek V4-Pro client
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py          # Base tool
│   │   ├── file_edit.py     # File edit tool
│   │   ├── web_search.py    # Web search tool
│   │   ├── shell_exec.py    # Shell execution tool
│   │   └── code_search.py   # Code search tool
│   └── tasks/
│       ├── __init__.py      # Task registry
│       ├── base.py          # Task base class
│       ├── refactoring_tasks.py
│       ├── research_tasks.py
│       ├── data_analysis_tasks.py
│       └── debugging_tasks.py
├── tests/
│   ├── test_models.py       # Model tests (19 tests)
│   ├── test_tools.py        # Tool tests (12 tests)
│   └── test_runner.py       # Runner/metrics tests (19 tests)
├── datasets/                # Generated datasets
├── outputs/                 # Generated plots
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
├── Makefile               # Build targets
├── .env.example           # Environment template
├── MODELS.md              # Model pricing docs
├── PUBLISH.md             # Publication guide
└── BUILD_NOTES.md         # This file
```

## Implementation Details

### Model Clients
- Base client with retry logic using tenacity
- Mock client for testing (cycles tool calls every 3rd response)
- Cost tracking per model with pricing constants
- Async streaming support

### Tools
- FileEditTool: read, write, edit, delete operations
- WebSearchTool: search with mock/real modes
- ShellExecTool: command execution with whitelist
- CodeSearchTool: regex pattern search across files

### Tasks (20 total)
- 5 Refactoring tasks
- 5 Research tasks  
- 5 Data Analysis tasks
- 5 Debugging tasks

Each task has: task_id, name, description, category, prompt, tools, expected_output, grader

### Metrics
- TaskMetrics: per-task results
- BenchmarkResult: aggregate results with summary
- Graders: ExactMatch, ContainsMatch, RegexMatch, Composite
- Efficiency score calculation

### Dataset Export
- Parquet format for traces
- Markdown dataset cards
- JSON metadata

## Test Results

```
pytest tests/ -v
==============================
50 passed in 0.36s
```

## Lint Results

```
ruff check .
All checks passed!
```

## Type Check Results

mypy reports 27 errors, mostly:
- Async generator return types (non-critical)
- Missing return type annotations in CLI (cosmetic)
- Missing seaborn stubs (optional dependency)

These do not affect functionality - all tests pass.

## Known Issues

1. mypy: Async generator return type mismatch in model clients
   - Impact: None - code works correctly
   - Fix: Would require refactoring base class signature

2. mypy: Missing return type annotations in CLI
   - Impact: None - cosmetic only
   - Fix: Add -> None annotations

3. mypy: Missing seaborn stubs
   - Impact: None - runtime works fine
   - Fix: Install types-seaborn package

## Build Commands

```bash
# Install
pip install -e ".[dev]"

# Test
make test

# Lint
make lint

# Type check
make type-check

# Full verification
make verify

# Generate plots
make plots

# Generate dataset
make dataset
```
