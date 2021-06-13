"""Award creation, viewing and editing."""
from typing import Any, Optional

from fastapi import Depends, Response

from pydantic import BaseModel

from .utils import auth_assert, authenticate, server
from ..models import Account, Award, Awardee, Scope, Team


class AwardCreateForm(BaseModel):
    """A form for creating a new award."""

    title: str
    image_url: str
    team: Team
    accounts: list[Account]


class AwardUpdateForm(BaseModel):
    """A form for updating an award."""

    title: Optional[str]
    image_url: Optional[str]
    team: Optional[Team]


@server.post('/awards/new', status_code=201, tags=['awards'])
async def create_award(
        data: AwardCreateForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new award."""
    auth_assert(scope.manage_awards)
    award = Award.create(
        title=data.title,
        image_url=data.image_url,
        team=data.team
    )
    done = set()
    for account in data.accounts:
        if account.id in done:
            continue
        done.add(account.id)
        Awardee.create(account=account, award=award)
    return award.as_dict()


@server.patch('/award/{award}', tags=['awards'])
async def update_award(
        award: Award,
        data: AwardUpdateForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Update an existing award."""
    auth_assert(scope.manage_awards)
    if data.title:
        award.title = data.title
    if data.image_url:
        award.image_url = data.image_url
    if data.team:
        award.team = data.team
    award.save()
    return award.as_dict()


@server.get('/award/{award}', tags=['awards'])
async def get_award(award: Award) -> dict[str, Any]:
    """Get an award."""
    team = award.team.as_dict() if award.team else None
    awardees = Account.select().join(Awardee).where(
        Awardee.award_id == award.id
    )
    return {
        'award': award.as_dict(),
        'awardees': [awardee.as_dict() for awardee in awardees],
        'team': team
    }


@server.delete('/award/{award}', status_code=204, tags=['awards'])
async def delete_award(
        award: Award,
        scope: Scope = Depends(authenticate)) -> Response:
    """Delete an award."""
    auth_assert(scope.manage_awards)
    award.delete_instance()
    return Response(status_code=204)


@server.put(
    '/account/{account}/award/{award}', status_code=201, tags=['awards']
)
async def give_award(
        account: Account,
        award: Award,
        scope: Scope = Depends(authenticate)) -> Response:
    """Assign an existing award to a specific user.

    An award may be assigned to multiple users.
    """
    auth_assert(scope.manage_awards)
    exists = Awardee.select().where(
        (Awardee.account_id == account.id)
        & (Awardee.award_id == award.id)
    ).limit(1).count()
    if exists:
        return Response(status_code=208)
    Awardee.create(award=award, account=account)
    return Response(status_code=201)


@server.delete(
    '/account/{account}/award/{award}', status_code=204, tags=['awards']
)
async def take_award(
        account: Account,
        award: Award,
        scope: Scope = Depends(authenticate)) -> Response:
    """Remove an award from a user."""
    auth_assert(scope.manage_awards)
    exists = Awardee.select().where(
        (Awardee.account_id == account.id)
        & (Awardee.award_id == award.id)
    ).limit(1).count()
    if not exists:
        return Response(status_code=404)
    Awardee.delete().where(
        (Awardee.account_id == account.id)
        & (Awardee.award_id == award.id)
    ).execute()
    return Response(status_code=204)
