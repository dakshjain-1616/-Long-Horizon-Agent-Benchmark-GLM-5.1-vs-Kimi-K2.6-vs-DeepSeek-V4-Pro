"""Metrics for evaluating agent performance."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""
    task_id: str
    model_name: str
    success: bool
    quality_score: float  # 0.0 to 1.0
    num_tool_calls: int
    total_tokens: int
    total_cost: float
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Complete benchmark results."""
    model_name: str
    task_results: List[TaskMetrics] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: TaskMetrics) -> None:
        """Add a task result."""
        self.task_results.append(result)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.task_results:
            return {"error": "No results available"}

        successes = [r for r in self.task_results if r.success]
        quality_scores = [r.quality_score for r in self.task_results]
        tool_calls = [r.num_tool_calls for r in self.task_results]
        costs = [r.total_cost for r in self.task_results]
        times = [r.execution_time for r in self.task_results]

        return {
            "model_name": self.model_name,
            "total_tasks": len(self.task_results),
            "successful_tasks": len(successes),
            "success_rate": len(successes) / len(self.task_results),
            "avg_quality_score": np.mean(quality_scores),
            "std_quality_score": np.std(quality_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "avg_tool_calls": np.mean(tool_calls),
            "std_tool_calls": np.std(tool_calls),
            "total_tool_calls": sum(tool_calls),
            "total_cost": sum(costs),
            "avg_cost": np.mean(costs),
            "avg_execution_time": np.mean(times),
            "total_execution_time": sum(times),
        }

    def quality_vs_calls(self) -> List[Dict[str, Any]]:
        """Get quality vs tool calls data for plotting."""
        return [
            {
                "task_id": r.task_id,
                "quality_score": r.quality_score,
                "num_tool_calls": r.num_tool_calls,
                "success": r.success,
                "cost": r.total_cost,
            }
            for r in self.task_results
        ]


class QualityGrader:
    """Base class for grading task quality."""

    def grade(self, output: str, expected: Optional[str] = None) -> float:
        """Grade the output quality. Returns score 0.0 to 1.0."""
        raise NotImplementedError


class ExactMatchGrader(QualityGrader):
    """Grader that checks for exact match."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def grade(self, output: str, expected: Optional[str] = None) -> float:
        """Grade by exact match."""
        if expected is None:
            return 0.0
        if self.case_sensitive:
            return 1.0 if output.strip() == expected.strip() else 0.0
        return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0


class ContainsMatchGrader(QualityGrader):
    """Grader that checks if output contains expected content."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def grade(self, output: str, expected: Optional[str] = None) -> float:
        """Grade by substring match."""
        if expected is None:
            return 0.0
        if self.case_sensitive:
            return 1.0 if expected in output else 0.0
        return 1.0 if expected.lower() in output.lower() else 0.0


class RegexMatchGrader(QualityGrader):
    """Grader that checks if output matches regex pattern."""

    def __init__(self, pattern: str) -> None:
        import re
        self.pattern = re.compile(pattern)

    def grade(self, output: str, expected: Optional[str] = None) -> float:
        """Grade by regex match."""
        return 1.0 if self.pattern.search(output) else 0.0


class CompositeGrader(QualityGrader):
    """Grader that combines multiple graders."""

    def __init__(self, graders: List[tuple[QualityGrader, float]]) -> None:
        """Initialize with list of (grader, weight) tuples."""
        self.graders = graders

    def grade(self, output: str, expected: Optional[str] = None) -> float:
        """Grade by weighted average of graders."""
        total_score = 0.0
        total_weight = 0.0
        for grader, weight in self.graders:
            total_score += grader.grade(output, expected) * weight
            total_weight += weight
        return total_score / total_weight if total_weight > 0 else 0.0


def calculate_efficiency_score(
    quality_score: float,
    num_tool_calls: int,
    baseline_calls: int = 10,
) -> float:
    """Calculate efficiency score based on quality and tool calls.

    Efficiency rewards high quality with fewer tool calls.
    """
    if num_tool_calls == 0:
        return quality_score
    call_penalty = min(num_tool_calls / baseline_calls, 1.0)
    return quality_score * (1.0 - call_penalty * 0.5)


def compare_models(
    results: List[BenchmarkResult],
) -> Dict[str, Any]:
    """Compare multiple model results."""
    if not results:
        return {"error": "No results to compare"}

    comparison = {
        "models": [r.model_name for r in results],
        "summaries": [r.get_summary() for r in results],
    }

    # Rank by different metrics
    summaries = comparison["summaries"]

    # Best by success rate
    best_success = max(summaries, key=lambda x: x.get("success_rate", 0))
    comparison["best_by_success_rate"] = best_success["model_name"]

    # Best by quality
    best_quality = max(summaries, key=lambda x: x.get("avg_quality_score", 0))
    comparison["best_by_quality"] = best_quality["model_name"]

    # Best by efficiency (quality per tool call)
    efficiencies = []
    for s in summaries:
        quality = s.get("avg_quality_score", 0)
        calls = s.get("avg_tool_calls", 1)
        efficiencies.append((s["model_name"], quality / max(calls, 1)))
    best_efficiency = max(efficiencies, key=lambda x: x[1])
    comparison["best_by_efficiency"] = best_efficiency[0]

    # Most cost-effective
    best_cost = min(summaries, key=lambda x: x.get("avg_cost", float("inf")))
    comparison["most_cost_effective"] = best_cost["model_name"]

    return comparison
