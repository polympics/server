"""Account creation, viewing and editing."""
from typing import Any, Optional, Union

from fastapi import BackgroundTasks, Depends, HTTPException, Response

import peewee

from pydantic import BaseModel

from .utils import Paginate, auth_assert, authenticate, server
from .. import discord
from ..config import SIGNUPS_OPEN
from ..models import Account, Callback, Event, ExplicitNone, Scope, Team


class SignupForm(BaseModel):
    """A form for creating a new account."""

    id: int
    name: str
    discriminator: str
    avatar_url: Optional[str] = None
    team: Optional[Team] = None
    permissions: int = 0


class AccountEditForm(BaseModel):
    """A form for editing an account."""

    name: Optional[str] = None
    discriminator: Optional[str] = None
    avatar_url: Optional[str] = None
    team: Optional[Union[Team, ExplicitNone]] = None
    grant_permissions: Optional[int] = None
    revoke_permissions: Optional[int] = None
    discord_token: Optional[str] = None


@server.get('/accounts/signups', tags=['accounts'])
async def signups_open() -> dict[str, Any]:
    """Check if signups are open."""
    return {'signups_open': SIGNUPS_OPEN}


@server.post('/accounts/new', status_code=201, tags=['accounts'])
async def signup(
        data: SignupForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new account."""
    if not SIGNUPS_OPEN:
        raise HTTPException(403, 'Signups are closed.')
    auth_assert(scope.manage_account_details)
    if data.permissions:
        auth_assert(scope.can_alter_permissions(data.team, data.permissions))
    try:
        account = Account.create(
            id=data.id, name=data.name,
            team=data.team, permissions=data.permissions,
            discriminator=data.discriminator, avatar_url=data.avatar_url
        )
    except peewee.IntegrityError:
        raise HTTPException(409, 'That Discord ID is already registered.')
    return account.as_dict()


@server.get('/accounts/search', tags=['accounts'])
async def search_for_account(
        q: str = None, team: Team = None,
        paginate: Paginate = Depends(Paginate)) -> list[dict[str, Any]]:
    """Search for accounts by name, team, both or neither."""
    query = Account.select().order_by(
        Account.name, Account.id
    )
    if q:
        query = query.where(Account.name ** f'%{q}%')
    if team:
        query = query.where(Account.team == team)
    return paginate(query)


@server.patch('/account/{account}', tags=['accounts'])
async def update_account(
        account: Account, data: AccountEditForm,
        background_tasks: BackgroundTasks,
        scope: Scope = Depends(authenticate)) -> Response:
    """Edit an account."""
    if data.name:
        auth_assert(scope.manage_account_details)
        account.name = data.name
    if data.discriminator:
        auth_assert(scope.manage_account_details)
        account.discriminator = data.discriminator
    if data.avatar_url:
        auth_assert(scope.manage_account_details)
        account.avatar_url = data.avatar_url
    if data.team:
        if isinstance(data.team, ExplicitNone):
            data.team = None
        kicking = (
            account.team
            and scope.owns_team(account.team)
            and data.team is None
        )
        joining = scope.account and scope.account.id == account.id
        auth_assert(scope.manage_account_teams or kicking or joining)
        account.team = data.team
        background_tasks.add_task(
            Callback.dispatch_event,
            Event.ACCOUNT_TEAM_UPDATE,
            {
                'account': account.as_dict(),
                'team': data.team.as_dict() if data.team else None
            }
        )
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
    if data.discord_token:
        try:
            user_data = await discord.get_user(data.discord_token)
        except ValueError:
            raise HTTPException(422, 'Bad Discord user token.')
        if user_data.id != account.id:
            raise HTTPException(
                403, 'Discord token is for a different account.'
            )
        account.name = user_data.name
        account.discriminator = user_data.discriminator
        account.avatar_url = user_data.avatar_url
    account.save()
    return account.as_dict()


@server.get('/account/{account}', tags=['accounts'])
async def get_account(account: Account) -> dict[str, Any]:
    """Get an account by ID."""
    return account.as_dict()


@server.delete('/account/{account}', status_code=204, tags=['accounts'])
async def delete_account(
        account: Account, scope: Scope = Depends(authenticate)) -> Response:
    """Delete an account."""
    auth_assert(scope.manage_account_details or scope.owns_account(account))
    account.delete_instance()
    return Response(status_code=204)
