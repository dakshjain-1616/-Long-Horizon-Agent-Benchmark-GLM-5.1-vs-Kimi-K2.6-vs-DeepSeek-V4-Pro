"""Debugging tasks for long-horizon benchmark."""

from ..metrics import ContainsMatchGrader
from .base import Task


class FixSyntaxErrorTask(Task):
    """Task to fix syntax errors in code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="fix_syntax_error",
            name="Fix Syntax Error",
            description="Identify and fix syntax errors in Python code",
            category="debugging",
            prompt='''Fix the syntax errors in the following Python code:

```python
def calculate_total(items)
    total = 0
    for item in items
        total += item['price'] * item['quantity']
    return total

def process_order(order)
    if order['type'] == 'standard'
        discount = 0.1
    elif order['type'] == 'premium'
        discount = 0.2
    else
        discount = 0

    total = calculate_total(order['items']
    final = total * (1 - discount)
    return final
```

Identify all syntax errors and provide the corrected code.''',
            tools=["file_edit"],
            expected_output="def",
            grader=ContainsMatchGrader(),
        )


class FindBugTask(Task):
    """Task to find and fix logical bugs."""

    def __init__(self) -> None:
        super().__init__(
            task_id="find_bug",
            name="Find Bug",
            description="Find and fix logical bugs in code",
            category="debugging",
            prompt='''Find and fix the bug in the following code:

```python
def find_max(numbers):
    """Find the maximum number in a list."""
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

# Test cases
print(find_max([1, 5, 3, 9, 2]))  # Expected: 9
print(find_max([-5, -2, -10]))    # Expected: -2, but returns 0!
```

The code has a logical bug. Identify it and provide the fix.''',
            tools=["file_edit"],
            expected_output="max",
            grader=ContainsMatchGrader(),
        )


class OptimizeCodeTask(Task):
    """Task to optimize slow code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="optimize_code",
            name="Optimize Code",
            description="Optimize inefficient code for better performance",
            category="debugging",
            prompt='''Optimize the following inefficient code:

```python
def find_duplicates(items):
    """Find duplicate items in a list."""
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

def count_occurrences(text, words):
    """Count occurrences of each word in text."""
    counts = {}
    for word in words:
        count = 0
        for w in text.split():
            if w == word:
                count += 1
        counts[word] = count
    return counts
```

The code works but is inefficient. Optimize both functions.''',
            tools=["file_edit"],
            expected_output="set",
            grader=ContainsMatchGrader(),
        )


class AddTestsTask(Task):
    """Task to add unit tests to untested code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="add_tests",
            name="Add Unit Tests",
            description="Add comprehensive unit tests to existing code",
            category="debugging",
            prompt='''Add unit tests for the following code:

```python
def validate_email(email):
    """Validate email format."""
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    return True

def calculate_area(shape, **kwargs):
    """Calculate area of geometric shapes."""
    if shape == 'rectangle':
        return kwargs['width'] * kwargs['height']
    elif shape == 'circle':
        import math
        return math.pi * kwargs['radius'] ** 2
    elif shape == 'triangle':
        return 0.5 * kwargs['base'] * kwargs['height']
    else:
        raise ValueError(f"Unknown shape: {shape}")
```

Write comprehensive pytest test cases covering normal cases, edge cases, and error cases.''',
            tools=["file_edit"],
            expected_output="def test",
            grader=ContainsMatchGrader(),
        )


class RefactorLegacyTask(Task):
    """Task to refactor legacy code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="refactor_legacy",
            name="Refactor Legacy Code",
            description="Refactor legacy code to modern Python standards",
            category="debugging",
            prompt='''Refactor the following legacy Python 2 style code to modern Python 3:

```python
# Legacy code with Python 2 patterns
import os, sys, json

def process_data(data):
    result = {}
    for key, value in data.iteritems():
        if type(value) == str:
            result[key] = value.upper()
        elif type(value) == int:
            result[key] = value * 2
        elif type(value) == dict:
            result[key] = process_data(value)
    return result

def read_file(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content

def write_file(filename, content):
    f = open(filename, 'w')
    f.write(content)
    f.close()
```

Modernize this code using Python 3 best practices including:
- Use .items() instead of .iteritems()
- Use isinstance() instead of type()
- Use context managers (with statement)
- Use modern type hints if appropriate''',
            tools=["file_edit"],
            expected_output="def",
            grader=ContainsMatchGrader(),
        )
