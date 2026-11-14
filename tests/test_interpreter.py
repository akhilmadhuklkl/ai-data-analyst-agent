import pytest

from ai_data_analyst.interpreter import InterpretationError, interpret_question
from ai_data_analyst.models import AnalysisIntent, ChartType

COLUMNS = ["product", "region", "revenue", "date"]


def test_interprets_grouped_revenue_question() -> None:
    request = interpret_question("Show revenue by region", COLUMNS)

    assert request.intent is AnalysisIntent.AGGREGATION
    assert request.metric_column == "revenue"
    assert request.group_by_column == "region"


def test_interprets_chart_and_top_limit() -> None:
    request = interpret_question("Create a bar chart of top 5 revenue by product", COLUMNS)

    assert request.chart_type is ChartType.BAR
    assert request.metric_column == "revenue"
    assert request.group_by_column == "product"
    assert request.result_limit == 5


def test_interprets_summary_question() -> None:
    request = interpret_question("Please summarise this dataset", COLUMNS)

    assert request.intent is AnalysisIntent.SUMMARY
    assert request.metric_column is None


def test_interprets_trend_over_time() -> None:
    request = interpret_question("Show the revenue trend over time", COLUMNS)

    assert request.intent is AnalysisIntent.TREND
    assert request.metric_column == "revenue"
    assert request.group_by_column == "date"


@pytest.mark.parametrize("question", ["", "Show the best result"])
def test_rejects_ambiguous_questions(question) -> None:
    with pytest.raises(InterpretationError):
        interpret_question(question, COLUMNS)
