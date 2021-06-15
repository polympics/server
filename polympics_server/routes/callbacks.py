"""Endpoints for managing an app's event callbacks."""
from typing import Any

from fastapi import Depends, HTTPException, Response

from pydantic import BaseModel, HttpUrl

from .utils import Scope, authenticate, server
from ..models import Callback, Event


class CallbackForm(BaseModel):
    """Form for creating a callback."""

    url: HttpUrl
    secret: str


def app_only(scope: Scope):
    """Terminate a request if it was not made by an app."""
    if not scope.app:
        raise HTTPException(401, 'Only apps may use this endpoint.')


@server.get('/callbacks', tags=['callbacks'])
async def get_callbacks(
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get callbacks for the authenticated app."""
    app_only(scope)
    callbacks = Callback.select().where(Callback.app_id == scope.app.id)
    data = {}
    for callback in callbacks:
        data[callback.event] = callback.url
    return {'callbacks': data}


@server.put('/callback/{event}', tags=['callbacks'])
async def create_callback(
        event: Event, data: CallbackForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a callback for the authenticated app for an event type.

    If a callback is already registered for this event type, it will be
    overwritten.
    """
    app_only(scope)
    existing = Callback.get_or_none(
        Callback.app_id == scope.app.id,
        Callback.event == event.value
    )
    if existing:
        existing.delete_instance()
    callback = Callback.create(
        app=scope.app, event=event.value, url=data.url, secret=data.secret
    )
    return callback.as_dict()


@server.get('/callback/{event}', tags=['callbacks'])
async def get_callback(
        event: Event,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get a callback for the authenticated app by event type."""
    app_only(scope)
    callback = Callback.get_or_none(
        Callback.app_id == scope.app.id,
        Callback.event == event.value
    )
    if not callback:
        raise HTTPException(404, 'No callback registered for this event.')
    return callback.as_dict()


@server.delete('/callback/{event}', status_code=204, tags=['callbacks'])
async def delete_callback(
        event: Event,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Delete a callback for the authenticated app."""
    app_only(scope)
    callback = Callback.get_or_none(
        Callback.app_id == scope.app.id,
        Callback.event == event.value
    )
    if not callback:
        raise HTTPException(404, 'No callback registered for this event.')
    callback.delete_instance()
    return Response(status_code=204)
