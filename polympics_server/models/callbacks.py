"""Models relating to event callbacks."""
import asyncio
import enum
from typing import Any

import peewee

from . import authentication
from .database import BaseModel, db
from .. import requests


class Event(str, enum.Enum):
    """A typing of event."""

    ACCOUNT_TEAM_UPDATE = 'account_team_update'


class Callback(BaseModel):
    """A callback for an event and app."""

    event = peewee.CharField(max_length=255)
    url = peewee.CharField(max_length=2047)
    secret = peewee.CharField(max_length=2047)
    app = peewee.ForeignKeyField(authentication.App, on_delete='CASCADE')

    @classmethod
    async def dispatch_event(cls, event: Event, data: dict[str, Any]):
        """Send an event to all apps subscribed to it."""
        session = await requests.get_session()
        tasks = []
        for callback in cls.select().where(cls.event == event.value):
            tasks.append(session.post(callback.url, json=data, headers={
                'Authorization': 'Bearer ' + callback.secret
            }))
        if tasks:
            # We don't care about the responses from the callbacks.
            await asyncio.wait(tasks, timeout=15)

    def as_dict(self) -> dict[str, Any]:
        """Get the callback as a dict to be returned as JSON."""
        return {
            'id': self.id,
            'event': self.event,
            'url': self.url
        }


db.create_tables([Callback])
