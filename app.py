"""Local Streamlit interface for the AI Data Analyst Agent."""

from pathlib import Path

import pandas as pd
import streamlit as st

from ai_data_analyst.analysis import AnalysisResult
from ai_data_analyst.application import ApplicationServices
from ai_data_analyst.data import DataValidationError, profile_dataframe
from ai_data_analyst.database import (
    SQLiteDatabase,
    SQLiteDatabaseError,
)
from ai_data_analyst.errors import AppError
from ai_data_analyst.interpretation import explain_result
from ai_data_analyst.models import AnalysisIntent, AnalysisRequest, ChartType
from ai_data_analyst.observability import configure_logging
from ai_data_analyst.visualization import create_chart

services = ApplicationServices()
configure_logging()

st.set_page_config(page_title="AI Data Analyst Agent", page_icon="📊", layout="wide")

st.title("📊 AI Data Analyst Agent")
st.caption("Upload a CSV, ask a question in plain English, and explore the result.")

interpreter_choice = st.radio(
    "Question interpreter",
    ["Rule-based (fast)", "Local AI with Ollama"],
    horizontal=True,
    help="The local AI option uses the Ollama model installed on this computer.",
)

data_source = st.radio(
    "Choose a data source",
    ["Upload a CSV", "Use sample dataset", "Upload SQLite database"],
    horizontal=True,
)

file_types = ["csv"] if data_source != "Upload SQLite database" else ["db", "sqlite", "sqlite3"]
uploaded_file = st.file_uploader("Upload a file", type=file_types)

if data_source == "Use sample dataset":
    sample_path = Path(__file__).parent / "examples" / "sample_sales.csv"
    dataframe = pd.read_csv(sample_path)
    st.success("Using the built-in sample sales dataset.")
elif data_source == "Upload SQLite database" and uploaded_file is not None:
    try:
        database = SQLiteDatabase.from_bytes(uploaded_file.getvalue())
        tables = list(database.schema())
        if not tables:
            st.error("This SQLite database does not contain any tables.")
            st.stop()
        selected_table = st.selectbox("Choose a table", tables)
        st.caption(f"Tables found: {', '.join(tables)}")
        dataframe = database.table_dataframe(selected_table)
        st.success(f"Using SQLite table: {selected_table}")
    except SQLiteDatabaseError as error:
        st.error(f"We could not open this database: {error}")
        st.stop()
elif uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
else:
    dataframe = None

if dataframe is None:
    st.info("Upload a CSV, choose the sample dataset, or upload a SQLite database to begin.")
    st.stop()

try:
    profile = profile_dataframe(dataframe)
except (DataValidationError, pd.errors.EmptyDataError, ValueError) as error:
    st.error(f"We could not use this dataset: {error}")
    st.stop()

with st.expander("Dataset profile", expanded=True):
    first, second, third = st.columns(3)
    first.metric("Rows", profile.row_count)
    second.metric("Columns", profile.column_count)
    third.metric("Missing values", sum(profile.missing_values.values()))
    st.dataframe(dataframe.head(10), use_container_width=True)

question_examples = [
    "Show revenue by region",
    "Create a bar chart of revenue by product",
    "Show the top 2 revenue by product",
    "Summarise this dataset",
]
question = st.text_input(
    "Ask a question about your data",
    placeholder="For example: Show revenue by region",
)
st.caption("Try one of these: " + " · ".join(question_examples))

if st.button("Analyse", type="primary", disabled=not question.strip()):
    with st.spinner("Analysing your data..."):
        try:
            if (
                data_source == "Upload SQLite database"
                and interpreter_choice == "Local AI with Ollama"
            ):
                database_result = services.analyze_database(database, question)
                st.subheader("Generated SQL")
                st.code(database_result.sql, language="sql")
                st.subheader("Database result")
                database_analysis = AnalysisResult(
                    intent=AnalysisIntent.AGGREGATION.value,
                    columns=database_result.dataframe.columns.tolist(),
                    rows=database_result.dataframe.to_dict(orient="records"),
                )
                database_request = AnalysisRequest(
                    question=question,
                    intent=AnalysisIntent.AGGREGATION,
                )
                st.info(explain_result(database_request, database_analysis))
                st.dataframe(database_result.dataframe, use_container_width=True)
                if "bar chart" in question.lower() and len(database_analysis.columns) >= 2:
                    chart = create_chart(database_analysis, ChartType.BAR)
                    st.plotly_chart(chart.figure, use_container_width=True)
            else:
                result = services.analyze_dataframe(
                    dataframe,
                    question,
                    use_local_ai=interpreter_choice == "Local AI with Ollama",
                )
                st.subheader("Analysis result")
                st.caption(f"Interpreted as: **{result.request.intent.value}**")
                st.info(result.explanation)
                st.dataframe(result.analysis.rows, use_container_width=True)
                if result.chart is not None:
                    st.plotly_chart(result.chart.figure, use_container_width=True)
        except (AppError, ValueError, KeyError) as error:
            st.error(f"I could not answer that question: {error}")
            st.info(
                "Try mentioning a metric and grouping column, for example: "
                "'Show revenue by region'."
            )
