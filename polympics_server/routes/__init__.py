"""Load the API routes and expose the application."""
from . import accounts, auth, teams    # noqa:F401
from .utils import server              # noqa:F401
