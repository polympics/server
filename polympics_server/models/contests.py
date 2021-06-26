"""Models for art contests and voting."""
import datetime
import enum
from typing import Any

import peewee

from .accounts import Account
from .database import BaseModel, db


class ContestState(enum.Enum):
    """The state of a contest."""

    UNOPENED = 'unopened'
    OPEN = 'open'
    CLOSED = 'closed'
    ENDED = 'ended'


class Contest(BaseModel):
    """A model for a single art contest."""

    title = peewee.CharField(max_length=255)
    description = peewee.CharField(max_length=2047)
    opens_at = peewee.DateTimeField()
    closes_at = peewee.DateTimeField()
    ends_at = peewee.DateTimeField()

    @property
    def state(self) -> ContestState:
        """Get the current state of the contest."""
        now = datetime.datetime.utcnow()
        if now > self.ends_at:
            return ContestState.ENDED
        if now > self.closes_at:
            return ContestState.CLOSED
        if now > self.opens_at:
            return ContestState.OPEN
        return ContestState.UNOPENED

    def as_dict(self) -> dict[str, Any]:
        """Get the contest as a dict to be returned as JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'opens_at': self.opens_at.timestamp(),
            'closes_at': self.closes_at.timestamp(),
            'ends_at': self.ends_at.timestamp(),
            'state': self.state
        }


class Submission(BaseModel):
    """A model for a submission to an art contest."""

    contest = peewee.ForeignKeyField(Contest)
    account = peewee.ForeignKeyField(Account)
    title = peewee.CharField(max_length=255)

    def as_dict(self, votes_and_author: bool = False) -> dict[str, Any]:
        """Get the contest as a dict to be returned as JSON."""
        pieces = Piece.select().where(Piece.submission == self).order_by(
            Piece.position
        )
        extra = {}
        if votes_and_author:
            if hasattr(self, 'vote_count'):
                extra['votes'] = self.vote_count
            else:
                extra['votes'] = Vote.select().where(
                    Vote.submission == self
                ).count()
            extra['author'] = self.account.as_dict()
        return {
            'id': self.id,
            'title': self.title,
            'pieces': [piece.as_dict() for piece in pieces],
            **extra
        }


class Piece(BaseModel):
    """An artwork (or other creative piece) that is part of a submission."""

    submission = peewee.ForeignKeyField(Submission)
    position = peewee.IntegerField()
    caption = peewee.CharField(max_length=255)
    mime_type = peewee.CharField(max_length=255)
    filename = peewee.CharField(max_length=255)
    data = peewee.BlobField()

    @property
    def url(self) -> str:
        """Get the URL from which this piece can be accessed."""
        return f'/uploads/pieces/{self.id}/{self.filename}'

    def as_dict(self) -> dict[str, Any]:
        """Get the piece as a dict to be returned as JSON."""
        return {
            'position': self.position,
            'caption': self.caption,
            'mime_type': self.mime_type,
            'filename': self.filename,
            'url': self.url
        }


class Vote(BaseModel):
    """A vote a user has placed on a submission."""

    account = peewee.ForeignKeyField(Account)
    submission = peewee.ForeignKeyField(Submission)


db.create_tables([Contest, Submission, Piece, Vote])
