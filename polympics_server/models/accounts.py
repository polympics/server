"""A model for a user account."""
from __future__ import annotations

from typing import Any

import peewee

from . import awards
from .database import BaseModel, db
from .teams import Team
from ..discord import DiscordUser


class Account(BaseModel):
    """A user account."""

    id = peewee.BigIntegerField(primary_key=True)
    name = peewee.CharField()
    discriminator = peewee.CharField()
    team = peewee.ForeignKeyField(
        Team, backref='members', null=True, on_delete='SET NULL'
    )
    avatar_url = peewee.CharField(max_length=512, null=True)
    permissions = peewee.BitField(default=0)

    manage_permissions = permissions.flag(1 << 0)
    manage_account_teams = permissions.flag(1 << 1)
    manage_account_details = permissions.flag(1 << 2)
    manage_teams = permissions.flag(1 << 3)
    # 1 << 4 is used for a different purpose by app permissions.
    manage_own_team = permissions.flag(1 << 5)
    manage_awards = permissions.flag(1 << 6)

    def as_dict(self) -> dict[str, Any]:
        """Get the account as a dict to be returned as JSON."""
        return {
            'id': str(self.id),
            'name': self.name,
            'discriminator': self.discriminator,
            'avatar_url': self.avatar_url,
            'team': self.team.as_dict() if self.team else None,
            'permissions': self.permissions,
            'created_at': self.created_at.timestamp(),
            'awards': [award.as_dict() for award in self.awards]
        }

    @classmethod
    def get_or_create_by_user(cls, user: DiscordUser) -> Account:
        """Get an account by ID or create one."""
        account = cls.get_or_none(cls.id == user.id)
        if account:
            return account
        return cls.create(
            id=user.id,
            name=user.name,
            discriminator=user.discriminator,
            avatar_url=user.avatar_url
        )

    @property
    def awards(self) -> list[awards.Award]:
        """Get a list of awards this player has won."""
        return list(
            awards.Award.select().join(
                awards.Awardee, peewee.JOIN.LEFT_OUTER
            ).where(awards.Awardee.account_id == self.id)
        )


db.create_tables([Account])
