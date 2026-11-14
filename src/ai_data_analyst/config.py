"""Application configuration helpers.

Secrets and environment-specific values will be added here as integrations are
introduced. Keeping configuration in one module prevents settings from being
scattered throughout the application.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings that are safe to read from environment variables."""

    app_name: str = "AI Data Analyst Agent"
    environment: str = "development"
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from environment variables with safe defaults."""

        return cls(
            environment=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
