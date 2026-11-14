import pytest

from ai_data_analyst.models import AnalysisIntent, AnalysisRequest, ChartType


def test_analysis_request_serializes_for_tool_calls() -> None:
    request = AnalysisRequest(
        question="  Show revenue by region  ",
        intent=AnalysisIntent.AGGREGATION,
        metric_column="revenue",
        group_by_column="region",
        chart_type=ChartType.BAR,
        result_limit=10,
    )

    assert request.question == "Show revenue by region"
    assert request.to_dict() == {
        "question": "Show revenue by region",
        "intent": "aggregation",
        "metric_column": "revenue",
        "group_by_column": "region",
        "chart_type": "bar",
        "result_limit": 10,
    }


def test_analysis_request_can_be_recreated_from_dict() -> None:
    request = AnalysisRequest.from_dict(
        {
            "question": "Find the sales trend",
            "intent": "trend",
            "chart_type": "line",
        }
    )

    assert request.intent is AnalysisIntent.TREND
    assert request.chart_type is ChartType.LINE


@pytest.mark.parametrize(
    ("field", "value"),
    [("question", "   "), ("metric_column", " "), ("group_by_column", "")],
)
def test_analysis_request_rejects_blank_values(field, value) -> None:
    values = {"question": "Analyse this data", field: value}

    with pytest.raises(ValueError, match="must not be"):
        AnalysisRequest(**values)


@pytest.mark.parametrize("result_limit", [0, 1_001])
def test_analysis_request_rejects_unsafe_result_limits(result_limit) -> None:
    with pytest.raises(ValueError, match="between 1 and 1000"):
        AnalysisRequest(question="Show results", result_limit=result_limit)
