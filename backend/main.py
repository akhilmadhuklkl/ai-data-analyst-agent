"""HTTP API for the AI Data Analyst Agent."""

from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ai_data_analyst.application import ApplicationServices
from ai_data_analyst.database import SQLiteDatabase, SQLiteDatabaseError
from ai_data_analyst.errors import AppError
from ai_data_analyst.observability import configure_logging

configure_logging()
services = ApplicationServices()
app = FastAPI(title="AI Data Analyst Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/analyze/csv")
async def analyze_csv(
    file: UploadFile = File(...),
    question: str = Form(...),
    use_local_ai: bool = Form(False),
) -> dict:
    try:
        dataframe = pd.read_csv(BytesIO(await file.read()))
        result = services.analyze_dataframe(dataframe, question, use_local_ai=use_local_ai)
        return result.to_dict()
    except (AppError, pd.errors.EmptyDataError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/analyze/sqlite")
async def analyze_sqlite(
    file: UploadFile = File(...),
    question: str = Form(...),
) -> dict:
    database = None
    try:
        database = SQLiteDatabase.from_bytes(await file.read())
        result = services.analyze_database(database, question)
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
