"""End-to-end orchestration for the current deterministic analysis workflow."""

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ai_data_analyst.analysis import AnalysisResult, analyze
from ai_data_analyst.interpreter import interpret_question
from ai_data_analyst.models import AnalysisRequest
from ai_data_analyst.visualization import ChartResult, create_chart


@dataclass(frozen=True)
class PipelineResult:
    """Complete response produced for one user question."""

    request: AnalysisRequest
    analysis: AnalysisResult
    chart: ChartResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a response suitable for an API or frontend."""

        return {
            "request": self.request.to_dict(),
            "analysis": self.analysis.to_dict(),
            "chart": self.chart.to_dict() if self.chart else None,
        }


def run_analysis(dataframe: pd.DataFrame, question: str) -> PipelineResult:
    """Interpret and execute a question against a dataframe."""

    request = interpret_question(question, dataframe.columns.tolist())
    analysis_result = analyze(dataframe, request)
    chart = (
        create_chart(analysis_result, request.chart_type)
        if request.chart_type is not None
        else None
    )
    return PipelineResult(request=request, analysis=analysis_result, chart=chart)
