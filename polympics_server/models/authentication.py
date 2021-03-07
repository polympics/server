"""A model for a user authentication session."""
from __future__ import annotations

import base64
import dataclasses
import os
from datetime import datetime
from typing import Any, Optional

import peewee

from .accounts import Account
from .database import BaseModel, db
from .teams import Team
from ..config import MAX_SESSION_AGE


def get_expires_time() -> datetime:
    """Get the time a session created now should expire."""
    return datetime.now() + MAX_SESSION_AGE


def generate_token() -> str:
    """Securely generate an authentication token."""
    return base64.b64encode(os.urandom(32)).decode()


class App(BaseModel):
    """An authentication option for a server.

    This provides authorisation all actions. It is intended for use
    by server-side services. An app should be created manually from the
    command line, and the token should be given to the operator of the
    service.
    """

    display_name = peewee.CharField()
    token = peewee.CharField(default=generate_token)
    permissions = peewee.BitField(default=0)

    manage_permissions = permissions.flag(1 << 0)
    manage_account_teams = permissions.flag(1 << 1)
    manage_account_details = permissions.flag(1 << 2)
    manage_teams = permissions.flag(1 << 3)
    authenticate_users = permissions.flag(1 << 4)

    def reset_token(self):
        """Reset the app's token."""
        self.token = generate_token()

    @property
    def scope(self) -> Scope:
        """Get the scope of the app."""
        return Scope(
            app=self,
            manage_permissions=self.manage_permissions,
            manage_account_teams=self.manage_account_teams,
            manage_account_details=self.manage_account_teams,
            manage_teams=self.manage_teams,
            authenticate_users=self.authenticate_users
        )

    @property
    def expired(self) -> bool:
        """Return False, because app tokens don't expire."""
        return False


class Session(BaseModel):
    """A user authentication session.

    This provides authorisation only for actions allowed for a certain user.
    It is intended for use by client side services. A session should be
    created by an App, and the token should be passed to the client.
    """

    account = peewee.ForeignKeyField(Account, backref='sessions')
    expires_at = peewee.DateTimeField(default=get_expires_time)
    token = peewee.CharField(default=generate_token)

    @property
    def expired(self) -> bool:
        """Return False, because app tokens don't expire."""
        return self.expires_at > datetime.now()

    @property
    def scope(self) -> Scope:
        """Get the scope of the session (the same as that of the account)."""
        return Scope(
            account=self.account,
            manage_permissions=self.account.manage_permissions,
            manage_account_teams=self.account.manage_account_teams,
            manage_account_details=self.account.manage_account_teams,
            manage_teams=self.account.manage_teams,
            manage_own_team=self.account.manage_own_team
        )

    def as_dict(self) -> dict[str, Any]:
        """Get the account as a dict to be returned as JSON."""
        return {
            'id': self.id,
            'token': self.token,
            'expires_at': self.expires_at.to_timestamp()
        }


@dataclasses.dataclass
class Scope:
    """Authorisation scope for the authenticated user/app."""

    account: Optional[Account] = None
    app: Optional[App] = None
    manage_permissions: bool = False
    manage_account_teams: bool = False
    manage_account_details: bool = False
    manage_teams: bool = False
    manage_own_team: bool = False
    authenticate_users: bool = False

    def owns_team(self, team: Team) -> bool:
        """Check if the scope is for an account that owns a given team."""
        return (
            self.account
            and self.account.team == team
            and self.account.manage_own_team
        )


db.create_tables([App, Session])
