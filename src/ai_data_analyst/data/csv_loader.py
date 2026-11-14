"""Load CSV files and create metadata for the analysis agent."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ai_data_analyst.errors import InputDataError


class DataValidationError(InputDataError):
    """Raised when an uploaded dataset cannot be analysed safely."""


@dataclass(frozen=True)
class DatasetProfile:
    """Compact description of a dataframe for the agent and user interface."""

    row_count: int
    column_count: int
    columns: list[str]
    dtypes: dict[str, str]
    missing_values: dict[str, int]
    preview: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of the profile."""

        return asdict(self)


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file after validating its path and basic structure."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise DataValidationError(f"CSV file does not exist: {csv_path}")
    if not csv_path.is_file():
        raise DataValidationError(f"CSV path is not a file: {csv_path}")
    if csv_path.suffix.lower() != ".csv":
        raise DataValidationError("Only .csv files are supported")

    try:
        dataframe = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as error:
        raise DataValidationError("The dataset is empty") from error
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise DataValidationError(f"Could not parse CSV file: {error}") from error

    return _validate_dataframe(dataframe)


def profile_dataframe(dataframe: pd.DataFrame, preview_rows: int = 5) -> DatasetProfile:
    """Create a compact, JSON-friendly profile of a dataframe."""

    dataframe = _validate_dataframe(dataframe)
    if preview_rows < 0:
        raise ValueError("preview_rows must be zero or greater")

    preview_frame = dataframe.head(preview_rows).astype(object)
    preview = preview_frame.where(preview_frame.notna(), None).to_dict(orient="records")
    return DatasetProfile(
        row_count=len(dataframe),
        column_count=len(dataframe.columns),
        columns=dataframe.columns.tolist(),
        dtypes={column: str(dtype) for column, dtype in dataframe.dtypes.items()},
        missing_values={column: int(count) for column, count in dataframe.isna().sum().items()},
        preview=preview,
    )


def _validate_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Validate dataframe conditions that would make downstream analysis ambiguous."""

    if dataframe.empty:
        raise DataValidationError("The dataset is empty")
    if dataframe.columns.empty:
        raise DataValidationError("The dataset has no columns")
    if dataframe.columns.duplicated().any():
        duplicates = dataframe.columns[dataframe.columns.duplicated()].tolist()
        raise DataValidationError(f"Duplicate column names are not supported: {duplicates}")

    return dataframe
