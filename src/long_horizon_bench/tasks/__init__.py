"""Task definitions for long-horizon benchmark."""


from .base import Task, TaskRegistry
from .data_analysis_tasks import (
    AnalyzeCSVTask,
    DataCleaningTask,
    GenerateReportTask,
    StatisticalAnalysisTask,
    VisualizationTask,
)
from .debugging_tasks import (
    AddTestsTask,
    FindBugTask,
    FixSyntaxErrorTask,
    OptimizeCodeTask,
    RefactorLegacyTask,
)

# Import all tasks
from .refactoring_tasks import (
    AddDocstringsTask,
    AddTypeHintsTask,
    ExtractClassTask,
    RefactorFunctionTask,
    RenameVariablesTask,
)
from .research_tasks import (
    CompareLibrariesTask,
    FindBestPracticeTask,
    FindDocumentationTask,
    ResearchAPIUsageTask,
    SummarizeArticleTask,
)

# Global TASKS dictionary for verification
TASKS: dict[str, Task] = {}

# Register all tasks
def _register_tasks() -> None:
    """Register all tasks in the global TASKS dictionary."""
    task_classes = [
        # Refactoring tasks
        RefactorFunctionTask,
        AddTypeHintsTask,
        ExtractClassTask,
        RenameVariablesTask,
        AddDocstringsTask,
        # Research tasks
        FindDocumentationTask,
        CompareLibrariesTask,
        FindBestPracticeTask,
        ResearchAPIUsageTask,
        SummarizeArticleTask,
        # Data analysis tasks
        AnalyzeCSVTask,
        GenerateReportTask,
        DataCleaningTask,
        StatisticalAnalysisTask,
        VisualizationTask,
        # Debugging tasks
        FixSyntaxErrorTask,
        FindBugTask,
        OptimizeCodeTask,
        AddTestsTask,
        RefactorLegacyTask,
    ]

    for task_class in task_classes:
        task = task_class()
        TASKS[task.task_id] = task

# Initialize TASKS
_register_tasks()

__all__ = [
    "Task",
    "TaskRegistry",
    "TASKS",
    # Refactoring
    "RefactorFunctionTask",
    "AddTypeHintsTask",
    "ExtractClassTask",
    "RenameVariablesTask",
    "AddDocstringsTask",
    # Research
    "FindDocumentationTask",
    "CompareLibrariesTask",
    "FindBestPracticeTask",
    "ResearchAPIUsageTask",
    "SummarizeArticleTask",
    # Data Analysis
    "AnalyzeCSVTask",
    "GenerateReportTask",
    "DataCleaningTask",
    "StatisticalAnalysisTask",
    "VisualizationTask",
    # Debugging
    "FixSyntaxErrorTask",
    "FindBugTask",
    "OptimizeCodeTask",
    "AddTestsTask",
    "RefactorLegacyTask",
]
