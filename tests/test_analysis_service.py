import pandas as pd
import pytest

from ai_data_analyst.analysis import AnalysisError, analyze
from ai_data_analyst.models import AnalysisIntent, AnalysisRequest


@pytest.fixture
def sales_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product": ["Laptop", "Phone", "Laptop", "Tablet"],
            "region": ["India", "India", "USA", "USA"],
            "revenue": [1000, 800, 1500, 500],
        }
    )


def test_summary_reports_numeric_and_missing_data(sales_data) -> None:
    result = analyze(sales_data, AnalysisRequest(question="Summarise the data"))

    revenue_row = next(row for row in result.rows if row["column"] == "revenue")
    assert revenue_row["mean"] == 950.0
    assert revenue_row["min"] == 500
    assert revenue_row["max"] == 1500


def test_aggregation_groups_and_sorts_by_metric(sales_data) -> None:
    request = AnalysisRequest(
        question="Show revenue by region",
        intent=AnalysisIntent.AGGREGATION,
        group_by_column="region",
        metric_column="revenue",
    )

    result = analyze(sales_data, request)

    assert result.columns == ["region", "total_revenue"]
    assert result.rows == [
        {"region": "USA", "total_revenue": 2000},
        {"region": "India", "total_revenue": 1800},
    ]


def test_aggregation_respects_result_limit(sales_data) -> None:
    request = AnalysisRequest(
        question="Show the top region",
        intent=AnalysisIntent.COMPARISON,
        group_by_column="product",
        metric_column="revenue",
        result_limit=1,
    )

    result = analyze(sales_data, request)

    assert len(result.rows) == 1
    assert result.rows[0]["product"] == "Laptop"


@pytest.mark.parametrize(
    ("group_by", "metric", "message"),
    [("missing", "revenue", "Unknown column"), ("region", "product", "must be numeric")],
)
def test_aggregation_rejects_invalid_columns(sales_data, group_by, metric, message) -> None:
    request = AnalysisRequest(
        question="Run an aggregation",
        intent=AnalysisIntent.AGGREGATION,
        group_by_column=group_by,
        metric_column=metric,
    )

    with pytest.raises(AnalysisError, match=message):
        analyze(sales_data, request)
