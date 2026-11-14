# AI Data Analyst Agent

An AI-powered data analyst that lets users upload CSV files or connect to a database, ask questions in plain English, and receive SQL, Python analysis, tables, and charts.

## Project status

🚧 In active development. Deployment will be added in a later phase.

## Planned capabilities

- Upload and inspect CSV data
- Connect to a database
- Ask data questions in natural language
- Generate and execute safe, read-only SQL
- Run controlled Python analysis
- Generate charts and explain results
- Recover from tool and data errors

## Development approach

This project is being built in small milestones. Each milestone will be tested, documented, committed, and pushed to GitHub.

## Local development

Create and activate a virtual environment, then install the development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[all]"
```

Run the test suite:

```powershell
python -m pytest
```

Run code-quality checks:

```powershell
python -m ruff check .
```

Application code lives in `src/ai_data_analyst/`. Tests live in `tests/`.

## Current data workflow

The data layer currently supports CSV files. It validates the file, loads it into a Pandas dataframe, and produces a dataset profile containing:

- Row and column counts
- Column names and detected data types
- Missing-value counts
- A small preview of the records

The analysis layer also defines a validated `AnalysisRequest`. This is the internal contract that will connect natural-language questions to SQL, Python, and chart tools.

The deterministic analysis service can currently execute summary and grouped aggregation requests. It returns structured rows that can later be rendered as tables or charts.

The visualization layer converts analysis results into serializable Plotly figures. The first supported chart types are bar, line, scatter, histogram, and table-style outputs.

## Roadmap

1. Project foundation and development standards
2. CSV ingestion and dataset profiling
3. Natural-language analysis workflow
4. Safe SQL tool
5. Python analysis tool
6. Chart generation
7. Agent orchestration and error recovery
8. Portfolio-quality UI and documentation
9. Deployment
