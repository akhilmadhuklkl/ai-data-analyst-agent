"""Create serializable Plotly charts from analysis results."""

from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.express as px

from ai_data_analyst.analysis import AnalysisResult
from ai_data_analyst.models import ChartType


class ChartError(ValueError):
    """Raised when a chart cannot be created from an analysis result."""


@dataclass(frozen=True)
class ChartResult:
    """Chart payload that can be sent to a frontend or saved as JSON."""

    chart_type: str
    title: str
    figure: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return the chart in a JSON-friendly format."""

        return {
            "chart_type": self.chart_type,
            "title": self.title,
            "figure": self.figure,
        }


def create_chart(
    result: AnalysisResult,
    chart_type: ChartType,
    title: str | None = None,
) -> ChartResult:
    """Create a Plotly chart from structured analysis rows."""

    if not result.rows:
        raise ChartError("Cannot create a chart from an empty result")

    dataframe = pd.DataFrame(result.rows)
    chart_title = title or f"{result.intent.title()} results"
    figure = _build_figure(dataframe, result.columns, chart_type, chart_title)
    return ChartResult(
        chart_type=chart_type.value,
        title=chart_title,
        figure=_json_safe(figure.to_dict()),
    )


def _build_figure(
    dataframe: pd.DataFrame,
    columns: list[str],
    chart_type: ChartType,
    title: str,
) -> Any:
    if chart_type is ChartType.TABLE:
        return px.bar(dataframe, title=title) if len(columns) < 2 else px.bar(
            dataframe, x=columns[0], y=columns[1], title=title
        )

    if len(columns) < 2:
        raise ChartError("At least two result columns are required for a chart")

    x_column, y_column = columns[0], columns[1]
    if chart_type is ChartType.BAR:
        return px.bar(dataframe, x=x_column, y=y_column, title=title)
    if chart_type is ChartType.LINE:
        return px.line(dataframe, x=x_column, y=y_column, title=title, markers=True)
    if chart_type is ChartType.SCATTER:
        return px.scatter(dataframe, x=x_column, y=y_column, title=title)
    if chart_type is ChartType.HISTOGRAM:
        return px.histogram(dataframe, x=y_column, title=title)

    raise ChartError(f"Unsupported chart type: {chart_type}")


def _json_safe(value: Any) -> Any:
    """Convert Plotly and NumPy containers into ordinary JSON values."""

    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value
