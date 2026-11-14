"""Integration checks for the local FastAPI endpoint handlers."""

from pathlib import Path

from backend.main import health, sample_data, sample_database


def test_health_endpoint() -> None:
    assert health()["status"] == "ok"


def test_sample_csv_endpoint_returns_csv() -> None:
    response = sample_data()
    assert response.media_type == "text/csv"
    assert Path(response.path).read_text(encoding="utf-8").startswith("date,product,region")


def test_sample_database_endpoint_returns_sqlite() -> None:
    response = sample_database()
    assert response.media_type == "application/x-sqlite3"
    assert response.body.startswith(b"SQLite format 3")


