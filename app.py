"""Local Streamlit interface for the AI Data Analyst Agent."""

import pandas as pd
import streamlit as st

from ai_data_analyst.data import DataValidationError, profile_dataframe
from ai_data_analyst.pipeline import run_analysis

st.set_page_config(page_title="AI Data Analyst Agent", page_icon="📊", layout="wide")

st.title("📊 AI Data Analyst Agent")
st.caption("Upload a CSV, ask a question in plain English, and explore the result.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to begin your analysis.")
    st.stop()

try:
    dataframe = pd.read_csv(uploaded_file)
    profile = profile_dataframe(dataframe)
except (DataValidationError, pd.errors.EmptyDataError, ValueError) as error:
    st.error(str(error))
    st.stop()

with st.expander("Dataset profile", expanded=True):
    first, second, third = st.columns(3)
    first.metric("Rows", profile.row_count)
    second.metric("Columns", profile.column_count)
    third.metric("Missing values", sum(profile.missing_values.values()))
    st.dataframe(dataframe.head(10), use_container_width=True)

question = st.text_input(
    "Ask a question about your data",
    placeholder="For example: Show revenue by region",
)

if st.button("Analyse", type="primary", disabled=not question.strip()):
    with st.spinner("Analysing your data..."):
        try:
            result = run_analysis(dataframe, question)
        except (ValueError, KeyError) as error:
            st.error(str(error))
        else:
            st.subheader("Analysis result")
            st.caption(f"Interpreted as: **{result.request.intent.value}**")
            st.dataframe(result.analysis.rows, use_container_width=True)
            if result.chart is not None:
                st.plotly_chart(result.chart.figure, use_container_width=True)
