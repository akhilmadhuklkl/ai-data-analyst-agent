"""Create concise explanations grounded in deterministic analysis results."""

from typing import Any

from ai_data_analyst.analysis import AnalysisResult
from ai_data_analyst.models import AnalysisIntent, AnalysisRequest


def explain_result(request: AnalysisRequest, result: AnalysisResult) -> str:
    """Explain a result using only values present in the result rows."""

    if not result.rows:
        return "The analysis completed, but it did not return any rows."

    if request.intent is AnalysisIntent.SUMMARY:
        return _explain_summary(result)
    return _explain_grouped_result(result)


def _explain_summary(result: AnalysisResult) -> str:
    numeric_columns = [
        row["column"]
        for row in result.rows
        if row.get("mean") is not None
    ]
    missing_total = sum(int(row.get("missing", 0)) for row in result.rows)
    return (
        f"The dataset contains information about {len(result.rows)} columns. "
        f"{len(numeric_columns)} columns contain numeric values, and there are "
        f"{missing_total} missing values across the dataset."
    )


def _explain_grouped_result(result: AnalysisResult) -> str:
    group_column, value_column = result.columns[:2]
    top_row = result.rows[0]
    top_group = _display_value(top_row.get(group_column))
    top_value = _display_value(top_row.get(value_column))
    group_count = len(result.rows)
    return (
        f"The highest result is {top_group} with {value_column.replace('_', ' ')} "
        f"of {top_value}. The analysis returned {group_count} group"
        f"{'s' if group_count != 1 else ''}."
    )


def _display_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}" if value % 1 else f"{value:,.0f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)
