import json

import pytest

from ai_data_analyst.analysis import AnalysisResult
from ai_data_analyst.models import ChartType
from ai_data_analyst.visualization import ChartError, create_chart


@pytest.fixture
def revenue_result() -> AnalysisResult:
    return AnalysisResult(
        intent="aggregation",
        columns=["region", "total_revenue"],
        rows=[
            {"region": "USA", "total_revenue": 2000},
            {"region": "India", "total_revenue": 1800},
        ],
    )


def test_create_bar_chart_returns_serializable_figure(revenue_result) -> None:
    chart = create_chart(revenue_result, ChartType.BAR, title="Revenue by Region")

    assert chart.chart_type == "bar"
    assert chart.title == "Revenue by Region"
    assert chart.figure["layout"]["title"]["text"] == "Revenue by Region"
    assert chart.figure["data"][0]["x"] == ["USA", "India"]
    assert chart.figure["data"][0]["y"]
    json.dumps(chart.to_dict())


def test_create_line_chart_adds_markers(revenue_result) -> None:
    chart = create_chart(revenue_result, ChartType.LINE)

    assert chart.figure["data"][0]["mode"] == "lines+markers"


def test_chart_rejects_empty_results() -> None:
    result = AnalysisResult(intent="summary", columns=["column"], rows=[])

    with pytest.raises(ChartError, match="empty result"):
        create_chart(result, ChartType.BAR)


def test_chart_rejects_single_column_results() -> None:
    result = AnalysisResult(intent="summary", columns=["value"], rows=[{"value": 1}])

    with pytest.raises(ChartError, match="two result columns"):
        create_chart(result, ChartType.BAR)
