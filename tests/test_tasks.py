"""Tests for tasks."""


import pytest

from long_horizon_bench.tasks import TASKS, Task, TaskRegistry
from long_horizon_bench.tasks.base import Task
from long_horizon_bench.tasks.data_analysis_tasks import AnalyzeCSVTask
from long_horizon_bench.tasks.debugging_tasks import FixSyntaxErrorTask
from long_horizon_bench.tasks.refactoring_tasks import RefactorFunctionTask
from long_horizon_bench.tasks.research_tasks import FindDocumentationTask


class TestTaskRegistry:
    def test_registry_creation(self) -> None:
        registry = TaskRegistry()
        assert registry.count() == 0

    def test_register_task(self) -> None:
        registry = TaskRegistry()
        task = RefactorFunctionTask()
        registry.register(task)
        assert registry.count() == 1
        assert registry.get("refactor_function") == task

    def test_get_by_category(self) -> None:
        registry = TaskRegistry()
        task = RefactorFunctionTask()
        registry.register(task)
        refactoring_tasks = registry.get_by_category("refactoring")
        assert len(refactoring_tasks) == 1
        assert refactoring_tasks[0].task_id == "refactor_function"


class TestGlobalTasks:
    def test_tasks_count(self) -> None:
        """Verify we have at least 20 tasks."""
        assert len(TASKS) >= 20

    def test_all_tasks_have_required_fields(self) -> None:
        for task_id, task in TASKS.items():
            assert task.task_id
            assert task.name
            assert task.description
            assert task.category
            assert task.prompt
            assert task.tools

    def test_task_categories(self) -> None:
        categories = set(task.category for task in TASKS.values())
        expected_categories = {"refactoring", "research", "data_analysis", "debugging"}
        assert categories == expected_categories


class TestRefactoringTasks:
    def test_refactor_function_task(self) -> None:
        task = RefactorFunctionTask()
        assert task.task_id == "refactor_function"
        assert task.category == "refactoring"
        assert "file_edit" in task.tools

    def test_add_type_hints_task(self) -> None:
        from long_horizon_bench.tasks.refactoring_tasks import AddTypeHintsTask
        task = AddTypeHintsTask()
        assert task.task_id == "add_type_hints"
        assert task.category == "refactoring"


class TestResearchTasks:
    def test_find_documentation_task(self) -> None:
        task = FindDocumentationTask()
        assert task.task_id == "find_documentation"
        assert task.category == "research"
        assert "web_search" in task.tools


class TestDataAnalysisTasks:
    def test_analyze_csv_task(self) -> None:
        task = AnalyzeCSVTask()
        assert task.task_id == "analyze_csv"
        assert task.category == "data_analysis"


class TestDebuggingTasks:
    def test_fix_syntax_error_task(self) -> None:
        task = FixSyntaxErrorTask()
        assert task.task_id == "fix_syntax_error"
        assert task.category == "debugging"


class TestTaskGrading:
    def test_contains_match_grader(self) -> None:
        task = RefactorFunctionTask()
        # Test grading with expected output
        score = task.grade("def process_data(): pass")
        assert score == 1.0

    def test_contains_match_grader_fail(self) -> None:
        task = RefactorFunctionTask()
        score = task.grade("class MyClass: pass")
        assert score == 0.0
