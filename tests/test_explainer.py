import pandas as pd

from ai_data_analyst.analysis import analyze
from ai_data_analyst.interpretation import explain_result
from ai_data_analyst.models import AnalysisIntent, AnalysisRequest


def test_explains_grouped_result_using_top_value() -> None:
    dataframe = pd.DataFrame(
        {"region": ["India", "USA"], "revenue": [1800, 1500]}
    )
    request = AnalysisRequest(
        question="Show revenue by region",
        intent=AnalysisIntent.AGGREGATION,
        group_by_column="region",
        metric_column="revenue",
    )

    result = analyze(dataframe, request)
    explanation = explain_result(request, result)

    assert "India" in explanation
    assert "1,800" in explanation
    assert "2 groups" in explanation


def test_explains_summary_missing_values() -> None:
    dataframe = pd.DataFrame({"product": ["Laptop", None], "revenue": [1000, 500]})
    request = AnalysisRequest(question="Summarise this dataset")

    result = analyze(dataframe, request)
    explanation = explain_result(request, result)

    assert "2 columns" in explanation
    assert "1 missing" in explanation
