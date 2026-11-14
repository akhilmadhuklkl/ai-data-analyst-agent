import pandas as pd
import pytest

from ai_data_analyst.database import SQLiteDatabase, SQLiteDatabaseError
from ai_data_analyst.errors import DatabaseFailure


@pytest.fixture
def database() -> SQLiteDatabase:
    with SQLiteDatabase() as connection:
        connection.load_dataframe(
            pd.DataFrame({"region": ["India", "USA"], "revenue": [1800, 1500]}),
            "sales",
        )
        yield connection


def test_schema_reports_loaded_table(database) -> None:
    assert database.schema() == {
        "sales": [
            {"name": "region", "type": "TEXT"},
            {"name": "revenue", "type": "INTEGER"},
        ]
    }


def test_query_returns_dataframe(database) -> None:
    result = database.query("SELECT region, revenue FROM sales ORDER BY revenue DESC")

    assert result.to_dict(orient="records") == [
        {"region": "India", "revenue": 1800},
        {"region": "USA", "revenue": 1500},
    ]


@pytest.mark.parametrize("sql", ["DELETE FROM sales", "DROP TABLE sales", "SELECT 1; SELECT 2"])
def test_query_rejects_unsafe_sql(database, sql) -> None:
    with pytest.raises(DatabaseFailure):
        database.query(sql)


def test_query_rejects_invalid_row_limit(database) -> None:
    with pytest.raises(SQLiteDatabaseError, match="max_rows"):
        database.query("SELECT * FROM sales", max_rows=0)


def test_uploaded_database_bytes_can_be_read(database) -> None:
    source = SQLiteDatabase()
    source.load_dataframe(pd.DataFrame({"value": [1, 2]}), "numbers")
    raw_bytes = source._connection.serialize()
    source.close()

    uploaded = SQLiteDatabase.from_bytes(raw_bytes)
    try:
        assert uploaded.table_dataframe("numbers").to_dict(orient="records") == [
            {"value": 1},
            {"value": 2},
        ]
    finally:
        uploaded.close()
