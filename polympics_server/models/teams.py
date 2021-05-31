"""A model for a team."""
from typing import Any

import peewee

from .database import BaseModel, db


class Team(BaseModel):
    """A team for a group of users."""

    name = peewee.CharField()

    def as_dict(self) -> dict[str, Any]:
        """Get the team as a dict to be returned as JSON."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.timestamp(),
            'member_count': self.members.count(),
            'awards': [award.as_dict() for award in self.awards]
        }


db.create_tables([Team])
