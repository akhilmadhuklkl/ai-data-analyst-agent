"""Logging configuration and safe request events."""

import logging

LOGGER_NAME = "ai_data_analyst"


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging once for local and deployed runtimes."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)


def get_logger(component: str) -> logging.Logger:
    """Return a namespaced logger for an application component."""

    return logging.getLogger(f"{LOGGER_NAME}.{component}")
