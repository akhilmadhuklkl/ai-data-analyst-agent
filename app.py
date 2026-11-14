"""Local Streamlit interface for the AI Data Analyst Agent."""

from pathlib import Path

import pandas as pd
import streamlit as st

from ai_data_analyst.ai import OllamaInterpreter
from ai_data_analyst.data import DataValidationError, profile_dataframe
from ai_data_analyst.pipeline import run_analysis

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
    ["Upload a CSV", "Use sample dataset"],
    horizontal=True,
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if data_source == "Use sample dataset":
    sample_path = Path(__file__).parent / "examples" / "sample_sales.csv"
    dataframe = pd.read_csv(sample_path)
    st.success("Using the built-in sample sales dataset.")
elif uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
else:
    dataframe = None

if dataframe is None:
    st.info("Upload a CSV file or choose the sample dataset to begin your analysis.")
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
            interpreter = (
                OllamaInterpreter().interpret
                if interpreter_choice == "Local AI with Ollama"
                else None
            )
            result = run_analysis(dataframe, question, interpreter=interpreter)
        except (ValueError, KeyError) as error:
            st.error(f"I could not answer that question: {error}")
            st.info(
                "Try mentioning a metric and grouping column, for example: "
                "'Show revenue by region'."
            )
        else:
            st.subheader("Analysis result")
            st.caption(f"Interpreted as: **{result.request.intent.value}**")
            st.info(result.explanation)
            st.dataframe(result.analysis.rows, use_container_width=True)
            if result.chart is not None:
                st.plotly_chart(result.chart.figure, use_container_width=True)
