"""Database-specific orchestration for generated SQL."""

from dataclasses import dataclass

import pandas as pd

from ai_data_analyst.ai.sql import OllamaSQLGenerator
from ai_data_analyst.database.sqlite import SQLiteDatabase


@dataclass(frozen=True)
class DatabaseQueryResult:
    """Generated SQL and the safe result returned by the database."""

    sql: str
    dataframe: pd.DataFrame


def run_database_question(
    database: SQLiteDatabase,
    question: str,
    generator: OllamaSQLGenerator | None = None,
) -> DatabaseQueryResult:
    """Generate and safely execute SQL for a database question."""

    sql = (generator or OllamaSQLGenerator()).generate(question, database.schema())
    return DatabaseQueryResult(sql=sql, dataframe=database.query(sql))
