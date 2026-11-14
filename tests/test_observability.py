import logging

from ai_data_analyst.observability import configure_logging, get_logger


def test_configure_logging_creates_namespaced_logger() -> None:
    configure_logging("DEBUG")

    logger = get_logger("test")

    assert logger.name == "ai_data_analyst.test"
    assert logger.isEnabledFor(logging.DEBUG)
