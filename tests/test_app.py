from pathlib import Path


def test_streamlit_entrypoint_exists() -> None:
    app_path = Path(__file__).parents[1] / "app.py"

    assert app_path.exists()
    assert "st.file_uploader" in app_path.read_text(encoding="utf-8")
    assert "run_analysis" in app_path.read_text(encoding="utf-8")
