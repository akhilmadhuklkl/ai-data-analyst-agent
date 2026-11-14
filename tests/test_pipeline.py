import json

import pandas as pd

from ai_data_analyst.models import AnalysisIntent, AnalysisRequest
from ai_data_analyst.pipeline import run_analysis


def test_pipeline_runs_question_to_analysis_result() -> None:
    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Phone", "Laptop"],
            "region": ["India", "India", "USA"],
            "revenue": [1000, 800, 1500],
        }
    )

    result = run_analysis(dataframe, "Show revenue by region")

    assert result.request.metric_column == "revenue"
    assert result.request.group_by_column == "region"
    assert result.analysis.rows == [
        {"region": "India", "total_revenue": 1800},
        {"region": "USA", "total_revenue": 1500},
    ]
    assert result.chart is None


def test_pipeline_adds_chart_when_requested() -> None:
    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Phone"],
            "revenue": [1000, 800],
        }
    )

    result = run_analysis(dataframe, "Create a bar chart of revenue by product")

    assert result.chart is not None
    assert result.chart.chart_type == "bar"
    json.dumps(result.to_dict())


def test_pipeline_accepts_a_custom_ai_interpreter() -> None:
    dataframe = pd.DataFrame({"region": ["India"], "revenue": [1000]})

    def fake_interpreter(question, columns):
        assert question == "What did India sell?"
        assert columns == ["region", "revenue"]
        return AnalysisRequest(
            question=question,
            intent=AnalysisIntent.AGGREGATION,
            group_by_column="region",
            metric_column="revenue",
        )

    result = run_analysis(dataframe, "What did India sell?", interpreter=fake_interpreter)

    assert result.analysis.rows == [{"region": "India", "total_revenue": 1000}]
