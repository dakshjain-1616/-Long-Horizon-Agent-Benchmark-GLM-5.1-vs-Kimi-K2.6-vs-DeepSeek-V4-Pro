# Long-Horizon Agent Benchmark

## Goal
Build a production-ready Python 3.11+ benchmark for evaluating long-horizon agent performance (50+ tool calls) across GLM-5.1, Kimi K2.6, and DeepSeek V4-Pro.

## Research Summary
- **Model IDs**: 
  - `THUDM/GLM-5.1` (Zhipu AI)
  - `moonshotai/Kimi-K2.6` (Moonshot AI)
  - `deepseek-v4-pro` (DeepSeek)
- **API Endpoints**: Verified OpenAI-compatible formats for Zhipu, Moonshot, and DeepSeek.
- **Constraints**: 20 tasks, 50+ tool calls per task, mock mode for CI/CD, structured JSONL tracing, and HF dataset preparation.

## Approach
1.  **Core Framework**: Implement a robust `Runner` that manages the agent loop, tool execution, and state persistence.
2.  **Task System**: Define 20 distinct tasks across refactoring, research, and data analysis. Use a base class for consistency.
3.  **Tooling**: Implement a suite of tools (file, search, shell, code) with both mock and real implementations.
4.  **Model Clients**: Create a unified interface for OpenAI-compatible providers with retries, timeouts, and cost tracking.
5.  **Evaluation**: Implement quality-over-time metrics and plotting using `matplotlib`.
6.  **Dataset**: Prepare a Parquet-based dataset schema for HuggingFace.

## Subtasks
1. **Scaffold Project Structure**: Create directories, `pyproject.toml`, `requirements.txt`, `Makefile`, and `.env.example`. (verify: `ls -R`)
2. **Implement Model Clients**: Build `models/` with support for GLM-5.1, Kimi K2.6, and DeepSeek V4-Pro. (verify: `pytest tests/test_models.py`)
3. **Implement Tools**: Build `tools/` (file, search, shell, code) with mock/real modes. (verify: `pytest tests/test_tools.py`)
4. **Implement Runner & Metrics**: Build `runner.py` and `metrics.py` to handle the agent loop and scoring. (verify: `pytest tests/test_runner.py`)
5. **Define 20 Tasks**: Implement all 20 task modules in `tasks/`. (verify: all files present and importable)
6. **CLI & Plotting**: Implement `cli.py` and `plots.py`. (verify: `make plots` produces PNGs)
7. **Dataset Generation**: Implement `make dataset` to produce Parquet + card. (verify: `datasets/` contains files)
8. **Final Polish**: Run `ruff`, `mypy`, and `pytest`. (verify: zero errors)
9. **Documentation**: Create `MODELS.md`, `PUBLISH.md`, and `BUILD_NOTES.md`.

## Deliverables
| File Path | Description |
|-----------|-------------|
| `src/long_horizon_bench/` | Core source code |
| `tests/` | Pytest suite |
| `datasets/` | HF dataset artifacts |
| `outputs/` | Benchmark plots |
| `Makefile` | Build and test automation |
| `BUILD_NOTES.md` | Handover notes |

## Evaluation Criteria
- 20 runnable tasks in `src/long_horizon_bench/tasks/`.
- `make test` passes (100% mocked).
- `make plots` and `make dataset` produce expected artifacts.
- Zero lint/type errors.
- Correct 2026 model IDs used throughout.

## Notes
- All tests and default runs use `--mock` to avoid API costs.
- Git remote added but not pushed.
