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
    port=config.DB_PORT,
    autorollback=True
)


class ExplicitNone:
    """Pydantic type that only matches the integer 0.

    This should be used in a Union, before a model class.
    """

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]:
        """Get pydantic validators."""
        yield cls.convert

    @classmethod
    def convert(cls, model_id: str) -> ExplicitNone:
        """Return an instance if the ID passed is 0."""
        # Still convert to int, so we catch things like `0.0`.
        try:
            model_id = int(model_id)
        except ValueError:
            raise ValueError('Invalid ID: must be int.')
        if model_id == 0:
            return ExplicitNone()
        raise ValueError('Should fall through to next type.')

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]):
        """Modify the pydantic schema for this data type."""
        field_schema.update(pattern='^0$', examples=[0])


class BaseModel(peewee.Model):
    """Base model to set default settings."""

    created_at = peewee.DateTimeField(default=datetime.utcnow)

    class Meta:
        """Peewee settings config."""

        use_legacy_table_names = False
        database = db

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]:
        """Get pydantic validators."""
        yield cls.convert

    @classmethod
    def convert(cls, model_id: str) -> BaseModel:
        """Get a model from an ID, or raise ValueError."""
        try:
            model_id = int(model_id)
        except ValueError:
            raise ValueError(f'Invalid {cls.__name__} ID: must be int.')
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
