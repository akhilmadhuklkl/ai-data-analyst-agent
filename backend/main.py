"""HTTP API for the AI Data Analyst Agent."""

import sqlite3
from io import BytesIO
import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from ai_data_analyst.application import ApplicationServices
from ai_data_analyst.database import SQLiteDatabase, SQLiteDatabaseError
from ai_data_analyst.errors import AppError
from ai_data_analyst.observability import configure_logging

configure_logging()
services = ApplicationServices()
app = FastAPI(title="AI Data Analyst Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "50")) * 1024 * 1024
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]


async def _read_upload(file: UploadFile, allowed_extensions: set[str]) -> bytes:
    """Validate an upload name and size before handing it to a parser."""

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValueError(f"Unsupported file type. Expected: {allowed}")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("File is too large. The maximum upload size is 50 MB.")
    if not content:
        raise ValueError("The uploaded file is empty.")
    return content


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-data-analyst-agent"}


@app.get("/sample-data")
def sample_data() -> FileResponse:
    return FileResponse(
        Path(__file__).resolve().parent.parent / "examples" / "sample_sales.csv",
        media_type="text/csv",
        filename="sample_sales.csv",
    )


@app.get("/sample-database")
def sample_database() -> Response:
    """Return a generated SQLite database for local demos."""
    sample_path = Path(__file__).resolve().parent.parent / "examples" / "sample_sales.csv"
    dataframe = pd.read_csv(sample_path)
    connection = sqlite3.connect(":memory:")
    try:
        dataframe.to_sql("sales", connection, index=False, if_exists="replace")
        return Response(
            connection.serialize(),
            media_type="application/x-sqlite3",
            headers={"Content-Disposition": "attachment; filename=sample_sales.sqlite"},
        )
    finally:
        connection.close()


@app.post("/analyze/csv")
async def analyze_csv(
    file: UploadFile = File(...),
    question: str = Form(...),
    use_local_ai: bool = Form(False),
) -> dict:
    try:
        dataframe = pd.read_csv(BytesIO(await _read_upload(file, {".csv"})))
        result = services.analyze_dataframe(dataframe, question, use_local_ai=use_local_ai)
        return result.to_dict()
    except (AppError, pd.errors.EmptyDataError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/analyze/sqlite")
async def analyze_sqlite(
    file: UploadFile = File(...),
    question: str = Form(...),
    table_name: str | None = Form(None),
) -> dict:
    database = None
    try:
        database = SQLiteDatabase.from_bytes(
            await _read_upload(file, {".db", ".sqlite", ".sqlite3"})
        )
        result = services.analyze_database(database, question, table_name=table_name)
        return {
            "sql": result.sql,
            "columns": result.dataframe.columns.tolist(),
            "rows": result.dataframe.to_dict(orient="records"),
            "tables": list(database.schema()),
        }
    except (AppError, SQLiteDatabaseError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        if database is not None:
            database.close()


@app.post("/inspect/sqlite")
async def inspect_sqlite(file: UploadFile = File(...)) -> dict:
    database = None
    try:
        database = SQLiteDatabase.from_bytes(
            await _read_upload(file, {".db", ".sqlite", ".sqlite3"})
        )
        schema = database.schema()
        return {"tables": list(schema), "schema": schema}
    except (AppError, SQLiteDatabaseError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        if database is not None:
            database.close()
