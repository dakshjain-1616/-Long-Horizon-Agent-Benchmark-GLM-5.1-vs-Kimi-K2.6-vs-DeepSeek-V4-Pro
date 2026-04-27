"""Data analysis tasks for long-horizon benchmark."""

from ..metrics import ContainsMatchGrader, RegexMatchGrader
from .base import Task


class AnalyzeCSVTask(Task):
    """Task to analyze a CSV file."""

    def __init__(self) -> None:
        super().__init__(
            task_id="analyze_csv",
            name="Analyze CSV File",
            description="Load and analyze a CSV file to extract insights",
            category="data_analysis",
            prompt='''Analyze the following CSV data structure:

File: sales_data.csv
Columns: date, product_id, quantity, price, region

Your task:
1. Write Python code to load and analyze the CSV
2. Calculate total sales by region
3. Find top 5 products by revenue
4. Calculate monthly trends
5. Identify any anomalies or outliers

Provide the analysis code and a summary of findings.''',
            tools=["file_edit", "shell_exec"],
            expected_output="pandas",
            grader=ContainsMatchGrader(),
        )


class GenerateReportTask(Task):
    """Task to generate a data report."""

    def __init__(self) -> None:
        super().__init__(
            task_id="generate_report",
            name="Generate Data Report",
            description="Generate a formatted report from data analysis results",
            category="data_analysis",
            prompt='''Generate a formatted report from the following data:

Data:
- Total users: 10,500
- Active users (last 30 days): 7,200
- New signups: 450
- Churn rate: 3.2%
- Revenue: $125,000

Your task:
1. Create a well-formatted report with sections
2. Include key metrics and their changes
3. Add insights and recommendations
4. Format for readability

Generate a professional report in markdown format.''',
            tools=["file_edit"],
            expected_output="#",
            grader=RegexMatchGrader(r"^#"),
        )


class DataCleaningTask(Task):
    """Task to clean messy data."""

    def __init__(self) -> None:
        super().__init__(
            task_id="clean_data",
            name="Clean Data",
            description="Clean and preprocess messy data",
            category="data_analysis",
            prompt='''Clean the following messy data:

Raw data:
```
Name,Age,Email,Phone
John Doe,25,john@email.com,555-1234
jane smith,30,JANE@EMAIL.COM,555.5678
Bob,thirty,bob@email.com,(555) 9012
Alice,28,alice@email.com,555-3456
,35,test@email.com,
```

Your task:
1. Standardize name capitalization
2. Convert age to integers, handle invalid values
3. Normalize email addresses to lowercase
4. Standardize phone number format
5. Handle missing values appropriately

Provide the cleaned data and the code used.''',
            tools=["file_edit"],
            expected_output="def",
            grader=ContainsMatchGrader(),
        )


class StatisticalAnalysisTask(Task):
    """Task to perform statistical analysis."""

    def __init__(self) -> None:
        super().__init__(
            task_id="statistical_analysis",
            name="Statistical Analysis",
            description="Perform statistical analysis on a dataset",
            category="data_analysis",
            prompt='''Perform statistical analysis on the following dataset:

Data: [23, 45, 67, 89, 12, 34, 56, 78, 90, 11, 22, 33, 44, 55, 66, 77, 88, 99, 100, 5]

Your task:
1. Calculate mean, median, mode
2. Calculate standard deviation and variance
3. Find quartiles and IQR
4. Identify outliers using IQR method
5. Calculate correlation with: [25, 50, 70, 85, 15, 30, 60, 80, 95, 10, 20, 35, 40, 50, 65, 75, 85, 95, 105, 8]

Provide the statistical summary and interpretation.''',
            tools=["file_edit", "shell_exec"],
            expected_output="mean",
            grader=ContainsMatchGrader(),
        )


class VisualizationTask(Task):
    """Task to create data visualizations."""

    def __init__(self) -> None:
        super().__init__(
            task_id="create_visualization",
            name="Create Visualization",
            description="Create data visualizations from a dataset",
            category="data_analysis",
            prompt='''Create visualizations for the following data:

Monthly sales data:
- Jan: 12000, Feb: 15000, Mar: 18000, Apr: 14000
- May: 22000, Jun: 25000, Jul: 28000, Aug: 26000
- Sep: 20000, Oct: 23000, Nov: 30000, Dec: 35000

Your task:
1. Create a line chart showing monthly trends
2. Create a bar chart comparing quarters
3. Add appropriate labels and titles
4. Save the visualizations

Provide the Python code using matplotlib or similar library.''',
            tools=["file_edit"],
            expected_output="matplotlib",
            grader=ContainsMatchGrader(),
        )
