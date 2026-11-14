"""Small deterministic interpreter for common data questions."""

import re

from ai_data_analyst.models import AnalysisIntent, AnalysisRequest, ChartType


class InterpretationError(ValueError):
    """Raised when a question cannot be mapped to the request contract."""


def interpret_question(question: str, columns: list[str]) -> AnalysisRequest:
    """Convert a simple natural-language question into an analysis request.

    This rule-based interpreter is intentionally conservative. It only returns
    requests when the referenced columns can be matched to the dataset schema.
    """

    normalized = question.strip().lower()
    if not normalized:
        raise InterpretationError("Question must not be empty")
    if not columns:
        raise InterpretationError("At least one dataset column is required")

    column_lookup = {column.lower(): column for column in columns}
    metric = _find_column(normalized, column_lookup, _metric_terms(normalized))
    group_by = _find_group_column(normalized, column_lookup)
    chart_type = _find_chart_type(normalized)

    if _is_summary_question(normalized):
        return AnalysisRequest(
            question=question,
            intent=AnalysisIntent.SUMMARY,
            chart_type=chart_type,
        )

    if group_by is None:
        raise InterpretationError(
            "Could not find a grouping column. Try a question such as 'show revenue by region'."
        )
    if metric is None:
        raise InterpretationError(
            "Could not find a metric column. Mention a numeric column such as revenue or sales."
        )

    intent = AnalysisIntent.TREND if _is_trend_question(normalized) else AnalysisIntent.AGGREGATION
    return AnalysisRequest(
        question=question,
        intent=intent,
        metric_column=metric,
        group_by_column=group_by,
        chart_type=chart_type,
        result_limit=_find_result_limit(normalized),
    )


def _metric_terms(question: str) -> list[str]:
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", question)


def _find_column(question: str, columns: dict[str, str], terms: list[str]) -> str | None:
    for term in terms:
        if term in columns:
            return columns[term]
    return None


def _find_group_column(question: str, columns: dict[str, str]) -> str | None:
    match = re.search(r"\bby\s+([a-zA-Z_][a-zA-Z0-9_]*)", question)
    if match and match.group(1) in columns:
        return columns[match.group(1)]
    if "over time" in question:
        for candidate in ("date", "datetime", "timestamp", "time", "month", "year"):
            if candidate in columns:
                return columns[candidate]
    return None


def _find_chart_type(question: str) -> ChartType | None:
    for phrase, chart_type in (
        ("bar chart", ChartType.BAR),
        ("line chart", ChartType.LINE),
        ("scatter plot", ChartType.SCATTER),
        ("histogram", ChartType.HISTOGRAM),
        ("table", ChartType.TABLE),
    ):
        if phrase in question:
            return chart_type
    return None


def _find_result_limit(question: str) -> int:
    match = re.search(r"\btop\s+(\d+)\b", question)
    return int(match.group(1)) if match else 20


def _is_summary_question(question: str) -> bool:
    return any(term in question for term in ("summarize", "summarise", "summary", "profile"))


def _is_trend_question(question: str) -> bool:
    return any(term in question for term in ("trend", "over time", "by month", "by year"))
