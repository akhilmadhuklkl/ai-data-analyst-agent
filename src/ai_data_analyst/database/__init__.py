"""Database connectivity and safe query utilities."""

from ai_data_analyst.database.sqlite import SQLiteDatabase, SQLiteDatabaseError

__all__ = ["SQLiteDatabase", "SQLiteDatabaseError"]
