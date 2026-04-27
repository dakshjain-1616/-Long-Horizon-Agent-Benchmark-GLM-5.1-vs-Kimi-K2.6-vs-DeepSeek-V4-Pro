"""Tests for dataset module."""


import os
from pathlib import Path

import pandas as pd
import pytest

from long_horizon_bench.dataset import (
    export_dataset,
    export_traces_to_parquet,
    generate_dataset_card,
    trace_to_dataframe,
)
from long_horizon_bench.runner import AgentTrace, TraceStep


def create_mock_trace(task_id: str = "test_task", model_name: str = "mock-model") -> AgentTrace:
    """Create a mock trace for testing."""
    trace = AgentTrace(
        task_id=task_id,
        model_name=model_name,
        start_time=0.0,
        total_tokens=100,
        total_cost=0.01,
        success=True,
    )
    trace.steps.append(TraceStep(
        step_number=0,
        timestamp=0.0,
        role="user",
        content="Test prompt",
    ))
    trace.steps.append(TraceStep(
        step_number=1,
        timestamp=1.0,
        role="assistant",
        content="Test response",
    ))
    return trace


class TestTraceToDataFrame:
    def test_empty_traces(self) -> None:
        df = trace_to_dataframe([])
        assert len(df) == 0
        # Empty dataframe may have no columns, just verify it's empty
        assert df.empty

    def test_single_trace(self) -> None:
        trace = create_mock_trace()
        df = trace_to_dataframe([trace])
        assert len(df) == 2  # 2 steps
        assert df["task_id"].iloc[0] == "test_task"
        assert df["model_name"].iloc[0] == "mock-model"


class TestExportTracesToParquet:
    def test_export_to_parquet(self, tmp_path) -> None:
        trace = create_mock_trace()
        output_path = tmp_path / "test.parquet"
        result_path = export_traces_to_parquet([trace], str(output_path))
        assert Path(result_path).exists()
        # Verify we can read it back
        df = pd.read_parquet(result_path)
        assert len(df) == 2


class TestGenerateDatasetCard:
    def test_generate_card(self, tmp_path) -> None:
        trace = create_mock_trace()
        output_path = tmp_path / "dataset_card.md"
        result_path = generate_dataset_card([trace], str(output_path))
        assert Path(result_path).exists()
        content = Path(result_path).read_text()
        assert "Long-Horizon Agent Benchmark Dataset" in content
        assert "**Total Traces**: 1" in content

    def test_generate_card_with_metadata(self, tmp_path) -> None:
        trace = create_mock_trace()
        output_path = tmp_path / "dataset_card.md"
        metadata = {"version": "1.0.0", "author": "test"}
        result_path = generate_dataset_card([trace], str(output_path), metadata)
        content = Path(result_path).read_text()
        assert '"version": "1.0.0"' in content


class TestExportDataset:
    def test_export_complete_dataset(self, tmp_path) -> None:
        trace = create_mock_trace()
        output_dir = tmp_path / "dataset"
        result = export_dataset([trace], str(output_dir))
        assert "parquet" in result
        assert "card" in result
        assert "metadata" in result
        assert Path(result["parquet"]).exists()
        assert Path(result["card"]).exists()
        assert Path(result["metadata"]).exists()
