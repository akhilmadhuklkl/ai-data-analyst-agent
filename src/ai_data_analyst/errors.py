"""Shared application error taxonomy."""


class AppError(Exception):
    """Base class for expected, user-facing application failures."""


class InputDataError(AppError):
    """The uploaded or connected data is invalid."""


class AnalysisFailure(AppError):
    """The requested analysis cannot be performed on the available data."""


class AIProviderError(AppError):
    """The configured AI provider failed or returned invalid output."""


class DatabaseFailure(AppError):
    """A database connection or query failed."""


class UnsafeQueryError(DatabaseFailure):
    """A query violated the read-only database policy."""
