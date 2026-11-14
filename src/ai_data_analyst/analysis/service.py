"""Execute validated analysis requests without language-model reasoning."""

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ai_data_analyst.errors import AnalysisFailure
from ai_data_analyst.models import AnalysisIntent, AnalysisRequest


class AnalysisError(AnalysisFailure):
    """Raised when a request cannot be executed against a dataset."""


@dataclass(frozen=True)
class AnalysisResult:
    """Tabular result returned by the deterministic analysis layer."""

    intent: str
    columns: list[str]
    rows: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly result for the API and chart layer."""

        return {"intent": self.intent, "columns": self.columns, "rows": self.rows}


def analyze(dataframe: pd.DataFrame, request: AnalysisRequest) -> AnalysisResult:
    """Execute a supported request against a dataframe."""

    if dataframe.empty:
        raise AnalysisError("Cannot analyse an empty dataset")

    if request.intent is AnalysisIntent.SUMMARY:
        return _summarize(dataframe, request)

    if request.intent in {
        AnalysisIntent.AGGREGATION,
        AnalysisIntent.COMPARISON,
        AnalysisIntent.TREND,
        AnalysisIntent.VISUALIZATION,
    }:
        return _aggregate(dataframe, request)

    raise AnalysisError(f"Unsupported analysis intent: {request.intent}")


def _summarize(dataframe: pd.DataFrame, request: AnalysisRequest) -> AnalysisResult:
    rows = []
    for column in dataframe.columns:
        series = dataframe[column]
        row: dict[str, Any] = {
            "column": column,
            "dtype": str(series.dtype),
            "non_null": int(series.notna().sum()),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            row.update(
                {
                    "min": _json_value(series.min()),
                    "max": _json_value(series.max()),
                    "mean": _json_value(series.mean()),
                }
            )
        rows.append(row)

    return AnalysisResult(
        intent=request.intent.value,
        columns=["column", "dtype", "non_null", "missing", "unique", "min", "max", "mean"],
        rows=rows,
    )


def _aggregate(dataframe: pd.DataFrame, request: AnalysisRequest) -> AnalysisResult:
    group_by = _required_column(dataframe, request.group_by_column, "group_by_column")
    metric = _required_column(dataframe, request.metric_column, "metric_column")
    if not pd.api.types.is_numeric_dtype(dataframe[metric]):
        raise AnalysisError(f"Metric column must be numeric: {metric}")

    grouped = (
        dataframe.groupby(group_by, dropna=False, as_index=False)[metric]
        .sum()
        .rename(columns={metric: f"total_{metric}"})
        .sort_values(f"total_{metric}", ascending=False)
        .head(request.result_limit)
    )
    grouped[group_by] = grouped[group_by].where(grouped[group_by].notna(), None)
    rows = grouped.to_dict(orient="records")
    return AnalysisResult(
        intent=request.intent.value,
        columns=[group_by, f"total_{metric}"],
        rows=rows,
    )


def _required_column(dataframe: pd.DataFrame, column: str | None, field_name: str) -> str:
    if not column:
        raise AnalysisError(f"{field_name} is required for this analysis")
    if column not in dataframe.columns:
        raise AnalysisError(f"Unknown column: {column}")
    return column


def _json_value(value: Any) -> Any:
    return None if pd.isna(value) else value.item() if hasattr(value, "item") else value
