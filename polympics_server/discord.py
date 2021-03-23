"""Integration with the Discord API.

This is responsible for using a user auth token to get user data.
"""
import dataclasses

import aiohttp

from .config import DISCORD_API_URL, DISCORD_CDN_URL


session: aiohttp.ClientSession = None

AVATAR_URL = f'{DISCORD_CDN_URL}/avatars/{{id}}/{{hash}}.png'


@dataclasses.dataclass
class DiscordUser:
    """Data on a Discord user from the Discord API."""

    id: str
    name: str
    avatar_url: str
    discriminator: str


async def get_session() -> session:
    """Get or create the aiohttp session."""
    global session
    if (not session) or session.closed:
        session = aiohttp.ClientSession()
    return session


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
            avatar_url=AVATAR_URL.format(id=data['id'], hash=data['avatar']),
            discriminator=data['discriminator']
        )
    except KeyError as e:
        raise ValueError('Unexpected Discord API response.') from e
    return user
