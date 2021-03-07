"""Account creation, viewing and editing."""
from typing import Any, Optional

from fastapi import Depends, HTTPException

import peewee

from pydantic import BaseModel

from .utils import Paginate, auth_assert, authenticate, server
from ..models import Account, Scope, Session, Team


class SignupForm(BaseModel):
    """A form for creating a new account."""

    discord_id: int
    display_name: str
    team: Team


class AccountEditForm(BaseModel):
    """A form for editing an account."""

    display_name: Optional[str] = None
    team: Optional[Team] = None


@server.post('/accounts/signup', status_code=201)
async def signup(
        data: SignupForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new account."""
    auth_assert(scope.manage_account_details)
    try:
        account = Account.create(
            discord_id=data.discord_id, display_name=data.display_name,
            team=data.team
        )
    except peewee.IntegrityError:
        raise HTTPException(409, 'That Discord ID is already registered.')
    return account.as_dict()


@server.get('/accounts/search')
async def search_for_account(
        q: str = None, team: Team = None,
        paginate: Paginate = Depends(Paginate)) -> list[dict[str, Any]]:
    """Search for accounts by name, team, both or neither."""
    query = Account.select().order_by(
        Account.display_name, Account.discord_id
    )
    if q:
        query = query.where(Account.display_name ** f'%{q}%')
    if team:
        query = query.where(Account.team == team)
    return paginate(query)


@server.get('/accounts/me')
async def authorised_account(
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get the account for the authorised member, if any."""
    if not scope.account:
        raise HTTPException(
            401, 'A user session was not used to authenticate.'
        )
    return scope.account.as_dict()


@server.patch('/account/{account}', status_code=204)
async def update_account(
        account: Account, data: AccountEditForm,
        scope: Scope = Depends(authenticate)):
    """Edit an account."""
    if data.display_name:
        auth_assert(scope.manage_account_details)
        account.display_name = data.display_name
    if data.team:
        auth_assert(scope.manage_account_teams or scope.owns_team(data.team))
        account.team = data.team
    account.save()


@server.get('/account/{account}')
async def get_account(account: Account) -> dict[str, Any]:
    """Get an account by ID."""
    return account.as_dict()


@server.delete('/account/{account}', status_code=204)
async def delete_account(
        account: Account, scope: Scope = Depends(authenticate)):
    """Delete an account."""
    auth_assert(scope.manage_account_details)
    account.delete_instance()


@server.post('/account/{account}/session', status_code=201)
async def create_session(
        account: Account,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create an authentication session for an account."""
    auth_assert(scope.authenticate_users)
    session = Session.create(account=account)
    return session.as_dict()


@server.post('/token/reset')
async def reset_token(
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Reset the token used to authenticate.

    Only applicable for apps.
    """
    if not scope.app:
        raise HTTPException(401, 'An app token was not used to authenticate.')
    scope.app.reset_token()
    scope.app.save()
    return scope.app.as_dict()
