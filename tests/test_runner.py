"""Tests for runner and metrics."""

import pytest

from long_horizon_bench.metrics import (
    BenchmarkResult,
    CompositeGrader,
    ContainsMatchGrader,
    ExactMatchGrader,
    QualityGrader,
    RegexMatchGrader,
    TaskMetrics,
    calculate_efficiency_score,
    compare_models,
)
from long_horizon_bench.models import MockModelClient
from long_horizon_bench.runner import AgentRunner, AgentTrace
from long_horizon_bench.tools import FileEditTool, WebSearchTool


class TestAgentRunner:
    @pytest.mark.asyncio
    async def test_runner_creation(self) -> None:
        model = MockModelClient()
        tools = [FileEditTool(mock_mode=True), WebSearchTool(mock_mode=True)]
        runner = AgentRunner(model_client=model, tools=tools, max_steps=10)
        assert runner.max_steps == 10
        assert len(runner.tools) == 2

    @pytest.mark.asyncio
    async def test_runner_stats(self) -> None:
        model = MockModelClient()
        tools = [FileEditTool(mock_mode=True)]
        runner = AgentRunner(model_client=model, tools=tools)
        stats = runner.get_stats()
        assert stats["max_steps"] == 50
        assert "file_edit" in stats["available_tools"]

    @pytest.mark.asyncio
    async def test_run_without_tools(self) -> None:
        model = MockModelClient()
        runner = AgentRunner(model_client=model, tools=[], max_steps=5)
        trace = await runner.run(
            task_id="test_task",
            prompt="Hello",
            system_prompt="You are a test assistant.",
        )
        assert trace.task_id == "test_task"
        assert trace.success is True
        assert len(trace.steps) > 0

    @pytest.mark.asyncio
    async def test_run_with_mock_tools(self) -> None:
        model = MockModelClient()
        tools = [FileEditTool(mock_mode=True), WebSearchTool(mock_mode=True)]
        runner = AgentRunner(model_client=model, tools=tools, max_steps=5)
        trace = await runner.run(
            task_id="test_task",
            prompt="Test with tools",
        )
        assert trace.task_id == "test_task"
        assert trace.total_tokens >= 0


class TestAgentTrace:
    def test_trace_to_dict(self) -> None:
        trace = AgentTrace(
            task_id="test",
            model_name="mock",
            start_time=1234567890.0,
        )
        trace.success = True
        trace.final_output = "test output"
        trace.end_time = 1234567895.0
        data = trace.to_dict()
        assert data["task_id"] == "test"
        assert data["success"] is True
        assert data["final_output"] == "test output"


class TestTaskMetrics:
    def test_task_metrics_creation(self) -> None:
        metrics = TaskMetrics(
            task_id="task1",
            model_name="mock",
            success=True,
            quality_score=0.95,
            num_tool_calls=5,
            total_tokens=100,
            total_cost=0.01,
            execution_time=1.5,
        )
        assert metrics.task_id == "task1"
        assert metrics.quality_score == 0.95


class TestBenchmarkResult:
    def test_empty_summary(self) -> None:
        result = BenchmarkResult(model_name="test")
        summary = result.get_summary()
        assert "error" in summary

    def test_summary_with_results(self) -> None:
        result = BenchmarkResult(model_name="test")
        result.add_result(TaskMetrics(
            task_id="t1",
            model_name="test",
            success=True,
            quality_score=0.9,
            num_tool_calls=5,
            total_tokens=100,
            total_cost=0.01,
            execution_time=1.0,
        ))
        result.add_result(TaskMetrics(
            task_id="t2",
            model_name="test",
            success=False,
            quality_score=0.5,
            num_tool_calls=10,
            total_tokens=200,
            total_cost=0.02,
            execution_time=2.0,
        ))
        summary = result.get_summary()
        assert summary["total_tasks"] == 2
        assert summary["success_rate"] == 0.5
        assert summary["avg_quality_score"] == 0.7

    def test_quality_vs_calls(self) -> None:
        result = BenchmarkResult(model_name="test")
        result.add_result(TaskMetrics(
            task_id="t1",
            model_name="test",
            success=True,
            quality_score=0.9,
            num_tool_calls=5,
            total_tokens=100,
            total_cost=0.01,
            execution_time=1.0,
        ))
        data = result.quality_vs_calls()
        assert len(data) == 1
        assert data[0]["quality_score"] == 0.9
        assert data[0]["num_tool_calls"] == 5


class TestGraders:
    def test_exact_match_grader(self) -> None:
        grader = ExactMatchGrader()
        assert grader.grade("hello", "hello") == 1.0
        assert grader.grade("hello", "world") == 0.0
        assert grader.grade("Hello", "hello") == 1.0  # case insensitive

    def test_exact_match_grader_case_sensitive(self) -> None:
        grader = ExactMatchGrader(case_sensitive=True)
        assert grader.grade("Hello", "hello") == 0.0

    def test_contains_match_grader(self) -> None:
        grader = ContainsMatchGrader()
        assert grader.grade("hello world", "world") == 1.0
        assert grader.grade("hello world", "foo") == 0.0

    def test_regex_match_grader(self) -> None:
        grader = RegexMatchGrader(r"\d+")
        assert grader.grade("abc123", None) == 1.0
        assert grader.grade("abc", None) == 0.0

    def test_composite_grader(self) -> None:
        grader1 = ExactMatchGrader()
        grader2 = ContainsMatchGrader()
        composite = CompositeGrader([(grader1, 0.5), (grader2, 0.5)])
        # Exact match gives 1.0, contains gives 1.0 -> avg 1.0
        assert composite.grade("hello", "hello") == 1.0


class TestEfficiencyScore:
    def test_efficiency_perfect(self) -> None:
        score = calculate_efficiency_score(1.0, 0)
        assert score == 1.0

    def test_efficiency_with_calls(self) -> None:
        score = calculate_efficiency_score(1.0, 10, baseline_calls=10)
        assert score == 0.5  # 1.0 * (1 - 0.5)

    def test_efficiency_fewer_calls(self) -> None:
        score = calculate_efficiency_score(1.0, 5, baseline_calls=10)
        assert score == 0.75  # 1.0 * (1 - 0.25)


class TestCompareModels:
    def test_compare_empty(self) -> None:
        result = compare_models([])
        assert "error" in result

    def test_compare_models(self) -> None:
        result1 = BenchmarkResult(model_name="model_a")
        result1.add_result(TaskMetrics(
            task_id="t1",
            model_name="model_a",
            success=True,
            quality_score=0.9,
            num_tool_calls=5,
            total_tokens=100,
            total_cost=0.01,
            execution_time=1.0,
        ))
        result2 = BenchmarkResult(model_name="model_b")
        result2.add_result(TaskMetrics(
            task_id="t1",
            model_name="model_b",
            success=True,
            quality_score=0.8,
            num_tool_calls=10,
            total_tokens=200,
            total_cost=0.02,
            execution_time=2.0,
        ))
        comparison = compare_models([result1, result2])
        assert len(comparison["models"]) == 2
        assert "best_by_quality" in comparison
