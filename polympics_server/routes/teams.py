"""Team creation, viewing and editing."""
from typing import Any

from fastapi import Depends, Response

from pydantic import BaseModel

from .utils import Paginate, auth_assert, authenticate, server
from ..models import Scope, Team


class TeamData(BaseModel):
    """Form for creating/editing a team."""

    name: str


@server.post('/teams/new', status_code=201, tags=['teams'])
async def create_team(
        data: TeamData,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new team."""
    auth_assert(scope.manage_teams)
    team = Team.create(name=data.name)
    return team.as_dict()


@server.get('/teams/search', tags=['teams'])
async def all_teams(
        q: str = None,
        paginate: Paginate = Depends(Paginate)) -> list[dict[str, Any]]:
    """Get all teams, optionally searching by name."""
    query = Team.select().order_by(Team.name, Team.id)
    if q:
        query = query.where(Team.name ** f'%{q}%')
    return paginate(query)


@server.get('/team/{team}', tags=['teams'])
async def get_team(team: Team) -> dict[str, Any]:
    """Get a team by ID."""
    return team.as_dict()


@server.patch('/team/{team}', tags=['teams'])
async def edit_team(
        team: Team, data: TeamData,
        scope: Scope = Depends(authenticate)) -> Response:
    """Edit a team's name."""
    auth_assert(scope.manage_teams or scope.owns_team(team))
    team.name = data.name
    team.save()
    return team.as_dict()


@server.delete('/team/{team}', status_code=204, tags=['teams'])
async def delete_team(
        team: Team, scope: Scope = Depends(authenticate)) -> Response:
    """Delete a team."""
    auth_assert(scope.manage_teams or scope.owns_team(team))
    team.delete_instance()
    return Response(status_code=204)
