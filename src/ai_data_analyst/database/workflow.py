"""Database-specific orchestration for generated SQL."""

from dataclasses import dataclass

import pandas as pd

from ai_data_analyst.database.sqlite import SQLiteDatabase
from ai_data_analyst.observability import get_logger


@dataclass(frozen=True)
class DatabaseQueryResult:
    """Generated SQL and the safe result returned by the database."""

    sql: str
    dataframe: pd.DataFrame


logger = get_logger("database")


def run_database_question(
    database: SQLiteDatabase,
    question: str,
    generator=None,
) -> DatabaseQueryResult:
    """Generate and safely execute SQL for a database question."""

    if generator is None:
        from ai_data_analyst.ai.sql import OllamaSQLGenerator

        generator = OllamaSQLGenerator()
    sql = generator.generate(question, database.schema())
    logger.info("database_query_generated sql_length=%d", len(sql))
    result = DatabaseQueryResult(sql=sql, dataframe=database.query(sql))
    logger.info("database_query_completed rows=%d", len(result.dataframe))
    return result
