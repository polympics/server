"""Peewee ORM models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Iterable

import peewee

from .. import config


db = peewee.PostgresqlDatabase(
    config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT
)


class BaseModel(peewee.Model):
    """Base model to set default settings."""

    created_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        """Peewee settings config."""

        use_legacy_table_names = False
        database = db

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]:
        """Get pydantic validators."""
        yield cls.convert

    @classmethod
    def convert(cls, model_id: int) -> BaseModel:
        """Get a model from an ID, or raise ValueError."""
        try:
            return cls.get_by_id(model_id)
        except peewee.DoesNotExist:
            raise ValueError(f'{cls.__name__} not found.')

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]):
        """Modify the pydantic schema for this data type."""
        field_schema.update(
            pattern='^[0-9]+$',
            examples=[13],
        )
