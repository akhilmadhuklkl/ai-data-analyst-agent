"""Generate safe read-only SQL with a local Ollama model."""

import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from ai_data_analyst.database import SQLiteDatabaseError, validate_read_only_sql


class SQLGenerationError(RuntimeError):
    """Raised when SQL generation or validation fails."""


@dataclass(frozen=True)
class OllamaSQLGenerator:
    """Generate one validated SQL query for a known SQLite schema."""

    model: str = "llama3.2:3b"
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: int = 120

    def generate(self, question: str, schema: dict) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Generate one SQLite read-only query. Return only JSON with a sql key. "
                        f"Schema: {json.dumps(schema)}. Never use INSERT, UPDATE, DELETE, DROP, "
                        "ALTER, CREATE, ATTACH, or DETACH."
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
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
            sql = json.loads(response_payload["message"]["content"])["sql"]
            validate_read_only_sql(sql)
        except SQLiteDatabaseError as error:
            raise SQLGenerationError(f"Generated SQL was rejected: {error}") from error
        except (OSError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise SQLGenerationError("Ollama returned invalid SQL") from error
        return sql
