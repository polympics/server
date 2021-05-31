"""Load the API routes and expose the application."""
from . import accounts, auth, awards, teams    # noqa:F401
from .utils import server                      # noqa:F401
