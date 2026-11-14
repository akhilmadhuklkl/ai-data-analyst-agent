from ai_data_analyst.ai import OllamaError, SQLGenerationError
from ai_data_analyst.analysis import AnalysisError
from ai_data_analyst.data import DataValidationError
from ai_data_analyst.database import SQLiteDatabaseError, validate_read_only_sql
from ai_data_analyst.errors import (
    AIProviderError,
    AnalysisFailure,
    AppError,
    DatabaseFailure,
    InputDataError,
    UnsafeQueryError,
)


def test_expected_errors_have_shared_categories() -> None:
    assert isinstance(DataValidationError("bad data"), InputDataError)
    assert isinstance(AnalysisError("bad analysis"), AnalysisFailure)
    assert isinstance(OllamaError("offline"), AIProviderError)
    assert isinstance(SQLGenerationError("unsafe"), AIProviderError)
    assert isinstance(SQLiteDatabaseError("database"), DatabaseFailure)


def test_unsafe_query_has_specific_category() -> None:
    try:
        validate_read_only_sql("DROP TABLE sales")
    except UnsafeQueryError as error:
        assert isinstance(error, AppError)
    else:
        raise AssertionError("Unsafe SQL was not rejected")
