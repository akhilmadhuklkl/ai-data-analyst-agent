import json

import pytest

from ai_data_analyst.ai import OllamaSQLGenerator, SQLGenerationError


class FakeResponse:
    def __init__(self, sql: str):
        self.sql = sql

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"message": {"content": json.dumps({"sql": self.sql})}}).encode()


def test_sql_generator_returns_valid_read_only_sql(monkeypatch) -> None:
    monkeypatch.setattr(
        "ai_data_analyst.ai.sql.urlopen",
        lambda *args, **kwargs: FakeResponse(
            "SELECT region, SUM(revenue) FROM sales GROUP BY region"
        ),
    )

    sql = OllamaSQLGenerator().generate("Show revenue by region", {"sales": []})

    assert sql.startswith("SELECT")


def test_sql_generator_rejects_write_sql(monkeypatch) -> None:
    monkeypatch.setattr(
        "ai_data_analyst.ai.sql.urlopen",
        lambda *args, **kwargs: FakeResponse("DROP TABLE sales"),
    )

    with pytest.raises(SQLGenerationError, match="rejected"):
        OllamaSQLGenerator().generate("Delete the table", {"sales": []})
