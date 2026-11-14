from ai_data_analyst import __version__
from ai_data_analyst.config import Settings


def test_package_has_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_use_development_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = Settings.from_environment()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
