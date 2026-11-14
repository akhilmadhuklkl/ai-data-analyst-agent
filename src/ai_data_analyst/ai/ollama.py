"""Ollama-backed structured request interpreter."""

import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from ai_data_analyst.errors import AIProviderError
from ai_data_analyst.models import AnalysisRequest
from ai_data_analyst.observability import get_logger


class OllamaError(AIProviderError):
    """Raised when the local Ollama service cannot produce a valid request."""


logger = get_logger("ollama")


@dataclass(frozen=True)
class OllamaInterpreter:
    """Convert questions into validated requests using a local Ollama model."""

    model: str = "llama3.2:3b"
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: int = 120

    def interpret(self, question: str, columns: list[str]) -> AnalysisRequest:
        """Ask Ollama for a request and validate its structured response."""

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You convert data questions into JSON. Return only JSON with these keys: "
                        "question, intent, metric_column, group_by_column, chart_type, "
                        "result_limit. "
                        f"Valid columns are: {columns}. For aggregation, metric_column must be "
                        "the numeric measure and group_by_column must be the category. "
                        "Valid intents: summary, aggregation, "
                        "trend, comparison, visualization. Valid chart types: bar, line, "
                        "scatter, histogram, "
                        "table, or null. Use null for unknown optional fields."
                    ),
                },
                {"role": "user", "content": question},
            ],
        }
        request = Request(
            f"{self.base_url.rstrip('/')}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            logger.info("ollama_request_started model=%s columns=%d", self.model, len(columns))
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError, json.JSONDecodeError) as error:
            raise OllamaError(f"Could not reach Ollama: {error}") from error

        try:
            content = response_payload["message"]["content"]
            values = json.loads(content)
            try:
                values["result_limit"] = int(values.get("result_limit", 20))
            except (TypeError, ValueError):
                values["result_limit"] = 20
            if values.get("chart_type") in {"", "none", "null"}:
                values["chart_type"] = None
            result = AnalysisRequest.from_dict(values)
            logger.info("ollama_request_completed intent=%s", result.intent.value)
            return result
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise OllamaError("Ollama returned an invalid analysis request") from error
