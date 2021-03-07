"""Read JSON config for the bot."""
import json
import logging
import pathlib
from datetime import timedelta


BASE_PATH = pathlib.Path(__file__).parent.parent

with open(str(BASE_PATH / 'config.json')) as f:
    config = json.load(f)


def get_log_level(field: str, default: int) -> int:
    """Parse a logging level field from the config file."""
    raw = config.get(field)
    if not raw:
        return default
    return {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'notset': logging.NOTSET,
        'none': logging.NOTSET
    }[raw.lower()]


def get_timedelta(field: str, default: timedelta) -> timedelta:
    """Parse a timedelta in config."""
    raw = config.get(field)
    if not raw:
        return default
    periods = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7,
        'M': 60 * 60 * 24 * 30,
        'y': 60 * 60 * 24 * 365
    }
    seconds = 0
    for part in raw.split():
        period_symbol = part[-1]
        value = int(part[:-1])
        seconds += value * periods[period_symbol]
    return timedelta(seconds=seconds)


DEBUG = config.get('debug', False)
MAX_SESSION_AGE = config.get('max_session_age', timedelta(minutes=30))

DB_NAME = config.get('db_name', 'polympics')
DB_USER = config.get('db_user', 'polympics')
DB_HOST = config.get('db_host', '127.0.0.1')
DB_PORT = config.get('db_port', 5432)
DB_PASSWORD = config['db_password']
DB_LOG_LEVEL = get_log_level('db_log_level', logging.INFO)
