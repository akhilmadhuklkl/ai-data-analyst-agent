import pandas as pd

from ai_data_analyst.application import ApplicationServices
from ai_data_analyst.database import SQLiteDatabase


def test_application_service_runs_csv_question_end_to_end() -> None:
    dataframe = pd.read_csv("examples/sample_sales.csv")

    result = ApplicationServices().analyze_dataframe(dataframe, "Show revenue by region")

    assert result.analysis.rows[0] == {"region": "India", "total_revenue": 21000}
    assert "India" in result.explanation


def test_application_service_runs_database_question_with_fake_generator() -> None:
    class FakeGenerator:
        def generate(self, question, schema):
            return "SELECT region, revenue FROM sales ORDER BY revenue DESC"

    with SQLiteDatabase() as database:
        database.load_dataframe(
            pd.DataFrame({"region": ["India"], "revenue": [21000]}),
            "sales",
        )
        result = database.query(FakeGenerator().generate("question", database.schema()))

    assert result.to_dict(orient="records") == [{"region": "India", "revenue": 21000}]
