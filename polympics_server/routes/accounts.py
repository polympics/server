"""Account creation, viewing and editing."""
from typing import Any, Optional

from fastapi import Depends, HTTPException, Response

import peewee

from pydantic import BaseModel

from .utils import Paginate, auth_assert, authenticate, server
from ..models import Account, Scope, Session, Team


class SignupForm(BaseModel):
    """A form for creating a new account."""

    discord_id: int
    display_name: str
    discriminator: int
    avatar_url: Optional[str] = None
    team: Optional[Team] = None
    permissions: int = 0


class AccountEditForm(BaseModel):
    """A form for editing an account."""

    display_name: Optional[str] = None
    discriminator: Optional[int] = None
    avatar_url: Optional[str] = None
    team: Optional[Team] = None
    grant_permissions: Optional[int] = None
    revoke_permissions: Optional[int] = None


@server.post('/accounts/signup', status_code=201)
async def signup(
        data: SignupForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new account."""
    auth_assert(scope.manage_account_details)
    if data.permissions:
        auth_assert(scope.can_alter_permissions(data.team, data.permissions))
    try:
        account = Account.create(
            discord_id=data.discord_id, display_name=data.display_name,
            team=data.team, permissions=data.permissions,
            discriminator=data.discriminator, avatar_url=data.avatar_url
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


@server.patch('/account/{account}')
async def update_account(
        account: Account, data: AccountEditForm,
        scope: Scope = Depends(authenticate)) -> Response:
    """Edit an account."""
    if data.display_name:
        auth_assert(scope.manage_account_details)
        account.display_name = data.display_name
    if data.discriminator:
        auth_assert(scope.manage_account_teams)
        account.discriminator = data.discriminator
    if data.avatar_url:
        auth_assert(scope.manage_account_details)
        account.avatar_url = data.avatar_url
    if data.team:
        auth_assert(scope.manage_account_teams or scope.owns_team(data.team))
        account.team = data.team
    if data.grant_permissions:
        auth_assert(scope.can_alter_permissions(
            account.team, data.grant_permissions
        ))
        account.permissions |= data.grant_permissions
    if data.revoke_permissions:
        auth_assert(scope.can_alter_permissions(
            account, data.revoke_permissions
        ))
        account.permissions &= ~data.revoke_permissions
    account.save()
    return account.as_dict()


@server.get('/account/{account}')
async def get_account(account: Account) -> dict[str, Any]:
    """Get an account by ID."""
    return account.as_dict()


@server.delete('/account/{account}', status_code=204)
async def delete_account(
        account: Account, scope: Scope = Depends(authenticate)) -> Response:
    """Delete an account."""
    auth_assert(scope.manage_account_details)
    account.delete_instance()
    return Response(status_code=204)


@server.post('/account/{account}/session', status_code=201)
async def create_session(
        account: Account,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create an authentication session for an account."""
    auth_assert(scope.authenticate_users)
    session = Session.create(account=account)
    return session.as_dict()


@server.post('/app/reset_token')
async def reset_token(scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Reset the token used to authenticate.

    Only applicable for apps.
    """
    if not scope.app:
        raise HTTPException(401, 'An app token was not used to authenticate.')
    scope.app.reset_token()
    scope.app.save()
    return scope.app.as_dict(with_token=True)


@server.get('/app')
async def get_app(scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get metadata on the authenticated app."""
    if not scope.app:
        raise HTTPException(401, 'An app token was not used to authenticate.')
    return scope.app.as_dict()
