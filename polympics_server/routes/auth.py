"""Endpoints related to user/app authentication."""
from typing import Any

from fastapi import Depends, HTTPException

from pydantic import BaseModel

from .utils import auth_assert, authenticate, server
from .. import discord
from ..models import Account, Scope, Session


class DiscordAuthData(BaseModel):
    """Form for creating a user session from a Discord user auth token."""

    token: str


class SessionData(BaseModel):
    """Form for creating a user session from an account."""

    account: Account


@server.post('/auth/create_session', status_code=201)
async def create_session(
        data: SessionData,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create an authentication session for an account."""
    auth_assert(scope.authenticate_users)
    session = Session.create(account=data.account)
    return session.as_dict()


@server.post('/auth/reset_token')
async def reset_token(scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Reset the token used to authenticate."""
    if scope.app:
        scope.app.reset_token()
        scope.app.save()
        return scope.app.as_dict(with_token=True)
    if scope.account_session:
        scope.account_session.reset_token()
        scope.account_session.save()
        return scope.account.as_dict()
    raise HTTPException(401, 'A token was not used to authenticate.')


@server.get('/auth/me')
async def get_app(scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get metadata on the authenticated app."""
    if scope.app:
        return scope.app.as_dict()
    if scope.account_session:
        return scope.account.as_dict()
    raise HTTPException(401, 'A token was not used to authenticate.')


@server.post('/auth/discord')
async def discord_authorise(data: DiscordAuthData) -> dict[str, Any]:
    """Create a user session using a Discord user auth token."""
    try:
        user_data = await discord.get_user(data.token)
    except ValueError:
        raise HTTPException(401, 'Bad Discord user token.')
    account = Account.get_or_create_by_user(user_data)
    session = Session.create(account=account)
    return session.as_dict()
