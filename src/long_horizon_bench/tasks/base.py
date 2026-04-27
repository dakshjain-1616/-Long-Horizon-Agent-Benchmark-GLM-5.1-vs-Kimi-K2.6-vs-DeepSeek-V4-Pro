"""Base task class for long-horizon benchmark."""

from dataclasses import dataclass, field
from typing import Any

from ..metrics import ContainsMatchGrader, QualityGrader


@dataclass
class Task:
    """A benchmark task definition."""
    task_id: str
    name: str
    description: str
    category: str  # "refactoring", "research", "data_analysis", "debugging"
    prompt: str
    tools: list[str]  # List of tool names required
    expected_output: str | None = None
    grader: QualityGrader | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default grader if not provided."""
        if self.grader is None:
            self.grader = ContainsMatchGrader()

    def grade(self, output: str) -> float:
        """Grade the task output."""
        if self.grader:
            return self.grader.grade(output, self.expected_output)
        return 0.0


class TaskRegistry:
    """Registry for benchmark tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        """Register a task."""
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        """List all registered tasks."""
        return list(self._tasks.values())

    def get_by_category(self, category: str) -> list[Task]:
        """Get tasks by category."""
        return [t for t in self._tasks.values() if t.category == category]

    def count(self) -> int:
        """Get total number of tasks."""
        return len(self._tasks)
