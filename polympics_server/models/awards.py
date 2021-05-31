"""Models for giving awards to players and their teams."""
from typing import Any

import peewee

from . import accounts
from .database import BaseModel, db
from .teams import Team


class Award(BaseModel):
    """An award given to a team."""

    title = peewee.CharField(max_length=32)
    image_url = peewee.CharField(max_length=512)
    team = peewee.ForeignKeyField(Team, null=True, backref='awards')

    def as_dict(self) -> dict[str, Any]:
        """Get the award as a dict to be returned as JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'image': self.image_url
        }


class Awardee(BaseModel):
    """A player who recieved an award.

    Can be multiple per award.
    """

    award = peewee.ForeignKeyField(Award)
    account = peewee.ForeignKeyField(accounts.Account)


db.create_tables([Award, Awardee])
