"""A model for a user account."""
from typing import Any

import peewee

from .database import BaseModel, db
from .teams import Team


class Account(BaseModel):
    """A user account."""

    discord_id = peewee.BigIntegerField(primary_key=True)
    display_name = peewee.CharField()
    team = peewee.ForeignKeyField(Team, backref='members')
    permissions = peewee.BitField(default=0)

    manage_permissions = permissions.flag(1 << 0)
    manage_account_teams = permissions.flag(1 << 1)
    manage_account_details = permissions.flag(1 << 2)
    manage_teams = permissions.flag(1 << 3)
    # 1 << 4 is used for a different purpose by app permissions.
    manage_own_team = permissions.flag(1 << 5)

    def as_dict(self) -> dict[str, Any]:
        """Get the account as a dict to be returned as JSON."""
        return {
            'discord_id': self.discord_id,
            'display_name': self.display_name,
            'team': self.team.as_dict(),
            'permissions': self.permissions,
            'created_at': self.created_at.to_timestamp()
        }


db.create_tables([Account])
