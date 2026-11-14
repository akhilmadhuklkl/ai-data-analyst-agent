from pathlib import Path


def test_streamlit_entrypoint_exists() -> None:
    app_path = Path(__file__).parents[1] / "app.py"

    assert app_path.exists()
    assert "st.file_uploader" in app_path.read_text(encoding="utf-8")
    assert "run_analysis" in app_path.read_text(encoding="utf-8")
    assert "Use sample dataset" in app_path.read_text(encoding="utf-8")
    assert "Show revenue by region" in app_path.read_text(encoding="utf-8")
    assert "Local AI with Ollama" in app_path.read_text(encoding="utf-8")
    assert "Upload SQLite database" in app_path.read_text(encoding="utf-8")
    assert "Generated SQL" in app_path.read_text(encoding="utf-8")
