"""Utility to keep a persistent aiohttp session."""
import aiohttp


session: aiohttp.ClientSession = None


async def get_session() -> session:
    """Get or create the aiohttp session."""
    global session
    if (not session) or session.closed:
        session = aiohttp.ClientSession()
    return session
