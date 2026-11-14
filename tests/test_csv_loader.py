import pandas as pd
import pytest

from ai_data_analyst.data import DataValidationError, load_csv, profile_dataframe


def test_profile_dataframe_returns_agent_metadata() -> None:
    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Phone", "Tablet"],
            "revenue": [1000, None, 500],
        }
    )

    profile = profile_dataframe(dataframe, preview_rows=2)

    assert profile.row_count == 3
    assert profile.column_count == 2
    assert profile.columns == ["product", "revenue"]
    assert profile.missing_values == {"product": 0, "revenue": 1}
    assert profile.preview[1]["revenue"] is None


def test_load_csv_reads_a_valid_file(tmp_path) -> None:
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text("product,revenue\nLaptop,1000\nPhone,800\n", encoding="utf-8")

    dataframe = load_csv(csv_path)

    assert dataframe.to_dict(orient="records") == [
        {"product": "Laptop", "revenue": 1000},
        {"product": "Phone", "revenue": 800},
    ]


@pytest.mark.parametrize("content", ["", "product,revenue\n"])
def test_load_csv_rejects_empty_datasets(tmp_path, content) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text(content, encoding="utf-8")

    with pytest.raises(DataValidationError, match="empty"):
        load_csv(csv_path)


def test_profile_rejects_duplicate_columns() -> None:
    dataframe = pd.DataFrame([[1, 2]], columns=["value", "value"])

    with pytest.raises(DataValidationError, match="Duplicate column"):
        profile_dataframe(dataframe)
