"""Expose the application to be run by an ASGI server."""
import logging

from . import config
from .routes import server as application    # noqa:F401


LOGS = (
    ('peewee', config.DB_LOG_LEVEL),
)
for log, level in LOGS:
    logger = logging.getLogger(log)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '{levelname}:{name}:{message}', style='{'
    ))
    logger.addHandler(handler)
    logger.setLevel(level)
