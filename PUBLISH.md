# Long-Horizon Agent Benchmark

A production-ready benchmark for evaluating long-horizon agent capabilities across multiple LLM providers.

## Overview

This benchmark evaluates agent performance on 20 tasks spanning refactoring, research, data analysis, and debugging. It supports multiple model providers (GLM-5.1, Kimi K2.6, DeepSeek V4-Pro) with comprehensive metrics, visualization, and dataset generation.

## Features

- **20 Tasks**: Covering refactoring, research, data analysis, and debugging
- **3 Model Providers**: GLM-5.1, Kimi K2.6, DeepSeek V4-Pro
- **4 Tools**: File edit, web search, shell execution, code search
- **Comprehensive Metrics**: Quality vs tool calls, cost tracking, success rates
- **Visualization**: Quality plots, cost distribution, success rates by category
- **Dataset Export**: Parquet format with dataset cards

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Run a Single Task

```bash
python -m long_horizon_bench.cli run --model mock --task refactor_function --mock
```

### Run Full Benchmark

```bash
python -m long_horizon_bench.cli benchmark --model mock --mock --output outputs/
```

### List Available Tasks

```bash
python -m long_horizon_bench.cli list-tasks
```

### List Supported Models

```bash
python -m long_horizon_bench.cli list-models
```

## Configuration

Copy `.env.example` to `.env` and configure API keys:

```bash
GLM_API_KEY=your_glm_key
KIMI_API_KEY=your_kimi_key
DEEPSEEK_API_KEY=your_deepseek_key
```

## Testing

```bash
make test
```

## Linting

```bash
make lint
```

## Type Checking

```bash
make type-check
```

## Project Structure

```
long_horizon_bench/
├── models/          # Model clients (GLM, Kimi, DeepSeek)
├── tools/           # Tool implementations
├── tasks/           # Task definitions (20 tasks)
├── runner.py        # Agent runner
├── metrics.py       # Metrics and grading
├── plots.py         # Visualization
├── dataset.py       # Dataset export
└── cli.py           # Command-line interface
```

## License

MIT License
