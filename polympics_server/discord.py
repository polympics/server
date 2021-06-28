"""Integration with the Discord API.

This is responsible for using a user auth token to get user data.
"""
import dataclasses
from typing import Any

from .config import DISCORD_API_URL, DISCORD_CDN_URL
from .requests import get_session


AVATAR_URL = f'{DISCORD_CDN_URL}/avatars/{{id}}/{{hash}}.png'
NO_AVATAR_URL = f'{DISCORD_CDN_URL}/embed/avatars/{{discrim}}.png'


@dataclasses.dataclass
class DiscordUser:
    """Data on a Discord user from the Discord API."""

    id: str
    name: str
    avatar_url: str
    discriminator: str


def get_avatar_url(data: dict[str, Any]) -> str:
    """Form the avatar URL of a user object."""
    if av_hash := data['avatar']:
        return AVATAR_URL.format(id=data['id'], hash=av_hash)
    return NO_AVATAR_URL.format(discriminator=data['discriminator'])


async def get_user(token: str) -> DiscordUser:
    """Get data on a user from an user token."""
    session = await get_session()
    headers = {'Authorization': 'Bearer ' + token}
    endpoint = DISCORD_API_URL + '/oauth2/@me'
    async with session.get(endpoint, headers=headers) as response:
        try:
            data = await response.json()
        except ValueError as e:
            raise ValueError('Unexpected Discord API response.') from e
    try:
        data = data['user']
        user = DiscordUser(
            id=int(data['id']),
            name=data['username'],
            avatar_url=get_avatar_url(data),
            discriminator=data['discriminator']
        )
    except KeyError as e:
        raise ValueError('Unexpected Discord API response.') from e
    return user
