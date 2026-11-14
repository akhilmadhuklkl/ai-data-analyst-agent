"""Structured requests used by the analysis workflow."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class AnalysisIntent(StrEnum):
    """High-level operation the analysis agent should perform."""

    SUMMARY = "summary"
    AGGREGATION = "aggregation"
    TREND = "trend"
    COMPARISON = "comparison"
    VISUALIZATION = "visualization"


class ChartType(StrEnum):
    """Supported chart preferences for the first analysis version."""

    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    TABLE = "table"


@dataclass(frozen=True)
class AnalysisRequest:
    """Validated, serializable instructions for one analysis request.

    The language model will eventually produce this structure. Keeping it
    separate from the model's raw response lets the application validate the
    request before executing SQL, Python, or chart-generation tools.
    """

    question: str
    intent: AnalysisIntent = AnalysisIntent.SUMMARY
    metric_column: str | None = None
    group_by_column: str | None = None
    chart_type: ChartType | None = None
    result_limit: int = 20

    def __post_init__(self) -> None:
        question = self.question.strip()
        if not question:
            raise ValueError("question must not be empty")
        object.__setattr__(self, "question", question)

        for field_name in ("metric_column", "group_by_column"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} must not be blank")

        if self.result_limit < 1 or self.result_limit > 1_000:
            raise ValueError("result_limit must be between 1 and 1000")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation for APIs and tool calls."""

        values = asdict(self)
        values["intent"] = self.intent.value
        values["chart_type"] = self.chart_type.value if self.chart_type else None
        return values

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "AnalysisRequest":
        """Build a validated request from model or API output."""

        data = dict(values)
        if "intent" in data and not isinstance(data["intent"], AnalysisIntent):
            data["intent"] = AnalysisIntent(data["intent"])
        if data.get("chart_type") is not None and not isinstance(data["chart_type"], ChartType):
            data["chart_type"] = ChartType(data["chart_type"])
        return cls(**data)
