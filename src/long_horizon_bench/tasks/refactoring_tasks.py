"""Refactoring tasks for long-horizon benchmark."""

from ..metrics import ContainsMatchGrader, RegexMatchGrader
from .base import Task


class RefactorFunctionTask(Task):
    """Task to refactor a monolithic function into smaller functions."""

    def __init__(self) -> None:
        super().__init__(
            task_id="refactor_function",
            name="Refactor Monolithic Function",
            description="Refactor a large monolithic function into smaller, more manageable functions",
            category="refactoring",
            prompt='''Refactor the following monolithic function into smaller, more manageable functions.

Code to refactor:
```python
def process_user_data(data):
    # This function does too much - validation, transformation, saving, logging
    if not data or 'user_id' not in data:
        raise ValueError("Invalid data")
    if 'email' not in data or '@' not in data['email']:
        raise ValueError("Invalid email")
    user_id = data['user_id']
    email = data['email'].lower().strip()
    name = data.get('name', '').strip().title()
    timestamp = datetime.now()
    log_entry = f"Processing user {user_id} at {timestamp}"
    with open('app.log', 'a') as f:
        f.write(log_entry + '\\n')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id, email, name) VALUES (?, ?, ?)', (user_id, email, name))
    conn.commit()
    conn.close()
    print(f"User {user_id} processed successfully")
    return {'user_id': user_id, 'email': email, 'name': name}
```

Break this into smaller functions with clear responsibilities.''',
            tools=["file_edit", "code_search"],
            expected_output="def",
            grader=ContainsMatchGrader(),
        )


class AddTypeHintsTask(Task):
    """Task to add type hints to untyped code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="add_type_hints",
            name="Add Type Hints",
            description="Add comprehensive type hints to Python code without type annotations",
            category="refactoring",
            prompt='''Add type hints to the following Python code:

```python
def calculate_discount(price, customer_type, years_member):
    if customer_type == "premium":
        discount = 0.2
    elif customer_type == "standard":
        discount = 0.1
    else:
        discount = 0.0

    if years_member > 5:
        discount += 0.05

    final_price = price * (1 - discount)
    return final_price

def process_order(items, customer_info):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']

    discount = calculate_discount(total, customer_info['type'], customer_info['years'])

    return {
        'total': total,
        'discount': discount,
        'final': total - discount
    }
```

Add proper type hints including imports from typing module.''',
            tools=["file_edit"],
            expected_output="->",
            grader=RegexMatchGrader(r"->\s*\w+"),
        )


class ExtractClassTask(Task):
    """Task to extract a class from procedural code."""

    def __init__(self) -> None:
        super().__init__(
            task_id="extract_class",
            name="Extract Class",
            description="Extract a class from procedural code with related data and functions",
            category="refactoring",
            prompt='''Extract a class from the following procedural code:

```python
# Current procedural approach
users = []

def create_user(name, email, age):
    user = {'id': len(users) + 1, 'name': name, 'email': email, 'age': age}
    users.append(user)
    return user

def update_user(user_id, name=None, email=None, age=None):
    for user in users:
        if user['id'] == user_id:
            if name: user['name'] = name
            if email: user['email'] = email
            if age: user['age'] = age
            return user
    return None

def delete_user(user_id):
    global users
    users = [u for u in users if u['id'] != user_id]

def get_user(user_id):
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def validate_email(email):
    return '@' in email and '.' in email.split('@')[1]

def validate_age(age):
    return isinstance(age, int) and 0 < age < 150
```

Convert this into a proper User class with methods.''',
            tools=["file_edit"],
            expected_output="class",
            grader=ContainsMatchGrader(),
        )


class RenameVariablesTask(Task):
    """Task to rename variables for clarity."""

    def __init__(self) -> None:
        super().__init__(
            task_id="rename_variables",
            name="Rename Variables",
            description="Rename poorly named variables to be more descriptive",
            category="refactoring",
            prompt='''Rename the variables in this code to be more descriptive:

```python
def calc(x, y, z):
    a = x * y
    b = a / z
    c = b * 0.15
    d = a + c
    return d

# Usage
r = calc(100, 5, 10)
print(r)
```

The variables should clearly indicate what they represent.''',
            tools=["file_edit", "code_search"],
            expected_output="price",
            grader=ContainsMatchGrader(),
        )


class AddDocstringsTask(Task):
    """Task to add docstrings to undocumented functions."""

    def __init__(self) -> None:
        super().__init__(
            task_id="add_docstrings",
            name="Add Docstrings",
            description="Add comprehensive docstrings to functions",
            category="refactoring",
            prompt='''Add docstrings to the following functions:

```python
def fetch_data(url, timeout=30):
    import requests
    response = requests.get(url, timeout=timeout)
    return response.json()

def parse_json(data):
    import json
    return json.loads(data)

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
```

Include parameter descriptions, return values, and examples.''',
            tools=["file_edit"],
            expected_output='"""',
            grader=RegexMatchGrader(r'"""'),
        )
