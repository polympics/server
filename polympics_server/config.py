"""Read JSON config for the bot."""
import json
import logging
import os
import pathlib
from datetime import timedelta


BASE_PATH = pathlib.Path(__file__).parent.parent

try:
    with open(str(BASE_PATH / 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    config = {key.lower(): value for key, value in os.environ.items()}


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


def get_bool(field: str, default: bool) -> bool:
    """Parse a boolean in config."""
    if field not in config:
        return default
    value = str(config.get(field)).lower()
    if value in ('1', 'true', 't', 'yes', 'y', 'on', 'enabled'):
        return True
    elif value in ('0', 'false', 'f', 'no', 'n', 'off', 'disabled'):
        return False
    else:
        raise ValueError(
            f'Unrecognised value for {field}, should be true or false.'
        )


def get_list(field: str, default: None) -> bool:
    """Parse a list of strings in config."""
    if field not in config:
        return default or []
    if isinstance(config[field], list):
        return config[field]
    return config[field].split(',')


DEBUG = get_bool('debug', False)
MAX_SESSION_AGE = get_timedelta('max_session_age', timedelta(days=30))
ALLOWED_ORIGINS = get_list('allowed_origins', [])

DB_NAME = config.get('db_name', 'polympics')
DB_USER = config.get('db_user', 'polympics')
DB_HOST = config.get('db_host', '127.0.0.1')
DB_PORT = config.get('db_port', 5432)
DB_PASSWORD = config['db_password']
DB_LOG_LEVEL = get_log_level('db_log_level', logging.INFO)

DISCORD_API_URL = config.get('discord_api_url', 'https://discord.com/api/v8')
DISCORD_CDN_URL = config.get('discord_cdn_url', 'https://cdn.discordapp.com')
