"""Utilities common to all the routes."""
import math
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import peewee

from .. import config
from ..models import App, Scope, Session


server = FastAPI(debug=config.DEBUG, title='Polympics API')
security = HTTPBasic()


class Paginate:
    """FastAPI dependency for parsing and using pagination options."""

    def __init__(self, page: int = 0, per_page: int = 20):
        """Store the options."""
        self.page = page
        self.per_page = per_page

    def __call__(self, query: peewee.SelectQuery) -> dict[str, Any]:
        """Apply the pagination options to a query and return the result."""
        total = query.count()
        total_pages = math.ceil(total / self.per_page)
        data = [
            record.as_json() for record in
            query.offset(self.page * self.per_page).limit(self.per_page)
        ]
        return {
            'page': self.page,
            'per_page': self.per_page,
            'pages': total_pages,
            'results': total,
            'data': data
        }


def authenticate(
        credentials: HTTPBasicCredentials = Depends(security)) -> Scope:
    """Check a username and password (RFC 7617) for authentication."""
    if credentials.username.upper().startswith('A'):
        model = App
    elif credentials.username.upper().startswith('S'):
        model = Session
    else:
        return None
    try:
        id = int(credentials.username[1:])
    except ValueError:
        return None
    session = model.get_or_none(
        (model.id == id) & (model.token == credentials.password)
    )
    if session.expired:
        session.delete_instance()
        return None
    return session.scope


def auth_assert(value: bool):
    """Make sure that the given value is truthy."""
    if not value:
        raise HTTPException(403, 'Request outside of authorisation scope.')
