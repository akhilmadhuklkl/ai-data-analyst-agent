import json

import pytest

from ai_data_analyst.ai import OllamaError, OllamaInterpreter
from ai_data_analyst.models import AnalysisIntent, ChartType


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "question": "Show revenue by region",
                            "intent": "aggregation",
                            "metric_column": "revenue",
                            "group_by_column": "region",
                            "chart_type": "bar",
                            "result_limit": 20,
                        }
                    )
                }
            }
        ).encode("utf-8")


def test_ollama_interpreter_validates_structured_response(monkeypatch) -> None:
    monkeypatch.setattr("ai_data_analyst.ai.ollama.urlopen", lambda *args, **kwargs: FakeResponse())

    request = OllamaInterpreter().interpret("Show revenue by region", ["region", "revenue"])

    assert request.intent is AnalysisIntent.AGGREGATION
    assert request.chart_type is ChartType.BAR
    assert request.metric_column == "revenue"


def test_ollama_interpreter_reports_invalid_response(monkeypatch) -> None:
    class InvalidResponse(FakeResponse):
        def read(self):
            return b'{"message":{"content":"not-json"}}'

    monkeypatch.setattr(
        "ai_data_analyst.ai.ollama.urlopen",
        lambda *args, **kwargs: InvalidResponse(),
    )

    with pytest.raises(OllamaError, match="invalid analysis request"):
        OllamaInterpreter().interpret("Show revenue by region", ["region", "revenue"])
