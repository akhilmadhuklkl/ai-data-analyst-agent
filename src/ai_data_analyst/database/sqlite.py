"""Safe SQLite access for local analysis workflows."""

import re
import sqlite3
from pathlib import Path

import pandas as pd


class SQLiteDatabaseError(ValueError):
    """Raised when a SQLite operation is invalid or fails."""


class SQLiteDatabase:
    """Small read-only query interface around a SQLite connection."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._connection = sqlite3.connect(self.path)

    @classmethod
    def from_bytes(cls, database_bytes: bytes) -> "SQLiteDatabase":
        """Create an in-memory database from an uploaded SQLite file."""

        database = cls()
        try:
            database._connection.deserialize(database_bytes)
        except sqlite3.Error as error:
            database.close()
            raise SQLiteDatabaseError(f"Could not open SQLite database: {error}") from error
        return database

    def close(self) -> None:
        """Close the underlying database connection."""

        self._connection.close()

    def __enter__(self) -> "SQLiteDatabase":
        return self

    def __exit__(self, *_args) -> None:
        self.close()

    def load_dataframe(self, dataframe: pd.DataFrame, table_name: str = "data") -> None:
        """Load a dataframe into a SQLite table for analysis."""

        _validate_identifier(table_name)
        if dataframe.empty:
            raise SQLiteDatabaseError("Cannot load an empty dataframe")
        dataframe.to_sql(table_name, self._connection, if_exists="replace", index=False)

    def schema(self) -> dict[str, list[dict[str, str]]]:
        """Return table and column metadata."""

        tables = self._connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
        return {
            table[0]: [
                {"name": column[1], "type": column[2] or "UNKNOWN"}
                for column in self._connection.execute(f'PRAGMA table_info("{table[0]}")')
            ]
            for table in tables
        }

    def query(self, sql: str, max_rows: int = 1_000) -> pd.DataFrame:
        """Execute one read-only SQL query with a row limit."""

        _validate_read_only_sql(sql)
        if max_rows < 1 or max_rows > 10_000:
            raise SQLiteDatabaseError("max_rows must be between 1 and 10000")

        try:
            result = pd.read_sql_query(sql, self._connection)
        except (pd.errors.DatabaseError, sqlite3.Error) as error:
            raise SQLiteDatabaseError(f"Query failed: {error}") from error
        return result.head(max_rows)

    def table_dataframe(self, table_name: str, max_rows: int = 10_000) -> pd.DataFrame:
        """Read one validated table into a dataframe."""

        if table_name not in self.schema():
            raise SQLiteDatabaseError(f"Unknown table: {table_name}")
        escaped_name = table_name.replace('"', '""')
        return self.query(f'SELECT * FROM "{escaped_name}"', max_rows=max_rows)


def _validate_identifier(identifier: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise SQLiteDatabaseError(f"Invalid table name: {identifier}")


def _validate_read_only_sql(sql: str) -> None:
    normalized = sql.strip().lower()
    if not normalized:
        raise SQLiteDatabaseError("SQL query must not be empty")
    if ";" in normalized.rstrip(";"):
        raise SQLiteDatabaseError("Only one SQL statement is allowed")
    if not normalized.startswith(("select", "with", "explain")):
        raise SQLiteDatabaseError("Only read-only SELECT, WITH, and EXPLAIN queries are allowed")
    if re.search(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach)\b", normalized):
        raise SQLiteDatabaseError("Write and schema-modifying SQL is not allowed")
