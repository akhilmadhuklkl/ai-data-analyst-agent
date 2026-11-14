import pandas as pd

from ai_data_analyst.database import SQLiteDatabase, run_database_question


class FakeSQLGenerator:
    def generate(self, question, schema):
        assert question == "Show revenue by region"
        assert "sales" in schema
        return "SELECT region, revenue FROM sales ORDER BY revenue DESC"


def test_database_workflow_returns_sql_and_rows() -> None:
    with SQLiteDatabase() as database:
        database.load_dataframe(
            pd.DataFrame({"region": ["India", "USA"], "revenue": [1800, 1500]}),
            "sales",
        )

        result = run_database_question(database, "Show revenue by region", FakeSQLGenerator())

    assert result.sql.startswith("SELECT")
    assert result.dataframe.to_dict(orient="records") == [
        {"region": "India", "revenue": 1800},
        {"region": "USA", "revenue": 1500},
    ]
