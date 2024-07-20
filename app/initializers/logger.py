from logging import config
from logging import getLogger

from app.settings import get_settings
settings = get_settings()


def get_logger():
    """Builds a logger with custom formatting."""
    config.dictConfig(settings.log_config)
    logger = getLogger(settings.app_name)
    return logger
