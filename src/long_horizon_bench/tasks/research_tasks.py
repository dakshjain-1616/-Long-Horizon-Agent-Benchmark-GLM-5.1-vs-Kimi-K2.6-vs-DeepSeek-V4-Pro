"""Research tasks for long-horizon benchmark."""

from ..metrics import ContainsMatchGrader
from .base import Task


class FindDocumentationTask(Task):
    """Task to find documentation for a library."""

    def __init__(self) -> None:
        super().__init__(
            task_id="find_documentation",
            name="Find Documentation",
            description="Find and summarize official documentation for a Python library",
            category="research",
            prompt='''Find the official documentation for the 'pydantic' library.

Your task:
1. Search for the official pydantic documentation
2. Find the main features and capabilities
3. Summarize the key concepts (models, validation, serialization)
4. Provide code examples for basic usage

Use web search to find the documentation, then provide a comprehensive summary.''',
            tools=["web_search"],
            expected_output="pydantic",
            grader=ContainsMatchGrader(),
        )


class CompareLibrariesTask(Task):
    """Task to compare two libraries."""

    def __init__(self) -> None:
        super().__init__(
            task_id="compare_libraries",
            name="Compare Libraries",
            description="Compare two similar Python libraries and recommend which to use",
            category="research",
            prompt='''Compare 'requests' and 'httpx' HTTP libraries for Python.

Your task:
1. Research both libraries using web search
2. Compare their features, performance, and use cases
3. Identify when to use each one
4. Provide code examples for common operations

Provide a recommendation with justification.''',
            tools=["web_search"],
            expected_output="requests",
            grader=ContainsMatchGrader(),
        )


class FindBestPracticeTask(Task):
    """Task to find best practices for a pattern."""

    def __init__(self) -> None:
        super().__init__(
            task_id="find_best_practices",
            name="Find Best Practices",
            description="Find best practices for a specific Python pattern or concept",
            category="research",
            prompt='''Find best practices for error handling in Python.

Your task:
1. Research Python error handling best practices
2. Cover: custom exceptions, exception hierarchy, logging, graceful degradation
3. Provide code examples showing good vs bad practices
4. Include guidelines for when to catch vs propagate exceptions

Provide comprehensive best practice recommendations.''',
            tools=["web_search"],
            expected_output="exception",
            grader=ContainsMatchGrader(),
        )


class ResearchAPIUsageTask(Task):
    """Task to research API usage patterns."""

    def __init__(self) -> None:
        super().__init__(
            task_id="research_api_usage",
            name="Research API Usage",
            description="Research how to use a specific API or service",
            category="research",
            prompt='''Research how to use the OpenAI API for chat completions.

Your task:
1. Find the official OpenAI API documentation
2. Understand the chat completions endpoint
3. Learn about parameters (model, messages, temperature, etc.)
4. Find code examples in Python
5. Understand rate limits and pricing

Provide a complete guide with working code examples.''',
            tools=["web_search"],
            expected_output="OpenAI",
            grader=ContainsMatchGrader(),
        )


class SummarizeArticleTask(Task):
    """Task to summarize a technical article."""

    def __init__(self) -> None:
        super().__init__(
            task_id="summarize_article",
            name="Summarize Article",
            description="Find and summarize a technical article on a specific topic",
            category="research",
            prompt='''Find and summarize an article about Python async/await and asyncio.

Your task:
1. Search for a recent, high-quality article on Python asyncio
2. Read and understand the key concepts
3. Summarize the main points
4. Extract practical code examples
5. Note any important caveats or best practices

Provide a concise but comprehensive summary.''',
            tools=["web_search"],
            expected_output="async",
            grader=ContainsMatchGrader(),
        )
