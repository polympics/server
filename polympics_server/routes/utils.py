"""Utilities common to all the routes."""
import math
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import peewee

from .. import config
from ..models import App, Scope, Session


server = FastAPI(
    debug=config.DEBUG,
    title='Polympics API',
    description='API server for the Polympics website.',
    version='0.6.1',
    openapi_tags=[
        {
            'name': 'accounts',
            'description': 'Endpoints for managing user accounts.'
        },
        {
            'name': 'teams',
            'description': 'Endpoints for managing user teams.'
        },
        {
            'name': 'awards',
            'description': 'Endpoints for managing awards.'
        },
        {
            'name': 'auth',
            'description': 'Endpoints relating to client authentication.'
        }
    ]
)
security = HTTPBasic()

server.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['Authorization', 'Content-Type'],
)


class Paginate:
    """FastAPI dependency for parsing and using pagination options."""

    def __init__(self, page: int = 0, per_page: int = 20):
        """Store the options."""
        self.page = page
        self.per_page = per_page

    def __call__(
            self,
            query: peewee.SelectQuery,
            **as_dict_args: Any) -> dict[str, Any]:
        """Apply the pagination options to a query and return the result."""
        total = query.count()
        total_pages = math.ceil(total / self.per_page)
        data = [
            record.as_dict(**as_dict_args) for record in
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
        return Scope()
    try:
        id = int(credentials.username[1:])
    except ValueError:
        return Scope()
    session = model.get_or_none(
        (model.id == id) & (model.token == credentials.password)
    )
    if not session:
        return Scope()
    if session.expired:
        session.delete_instance()
        return Scope()
    return session.scope


def auth_assert(value: bool):
    """Make sure that the given value is truthy."""
    if not value:
        raise HTTPException(403, 'Request outside of authorisation scope.')
