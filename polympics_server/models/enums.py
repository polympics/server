"""Tools for handling enums in database fields."""
from __future__ import annotations

import enum
import re
from typing import Any

import peewee


class BaseEnum(enum.Enum):
    """Base class to provide utilities to enums."""

    @classmethod
    def search(cls, query: str) -> list[BaseEnum]:
        """Search for an option by name."""
        argument = re.sub('[^A-Z]', '', query.upper())
        matches = []
        for option in cls:
            if option.name.replace('_', '').startswith(argument):
                matches.append(option)
        return matches

    def __str__(self) -> str:
        """Get a human-readable representation of the enum."""
        return self.name.title().replace('_', ' ')


class EnumField(peewee.SmallIntegerField):
    """A field where each value is an integer representing an option."""

    def __init__(
            self, options: enum.Enum, **kwargs: dict[str, Any]):
        """Create a new enum field."""
        self.options = options
        super().__init__(**kwargs)

    def python_value(self, raw: int) -> enum.Enum:
        """Convert a raw number to an enum value."""
        if raw is None:
            return None
        number = super().python_value(raw)
        return self.options(number)

    def db_value(self, instance: enum.Enum) -> int:
        """Convert an enum value to a raw number."""
        if instance is None:
            return super().db_value(None)
        if not isinstance(instance, self.options):
            raise TypeError(f'Instance is not of enum class {self.options}.')
        number = instance.value
        return super().db_value(number)
