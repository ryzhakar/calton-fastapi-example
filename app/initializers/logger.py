from logging import config
from logging import getLogger

from app.settings import get_settings


def get_logger(name: str):
    """Builds a logger with custom formatting."""
    config.dictConfig(get_settings().log_config)
    logger = getLogger(name)
    return logger
