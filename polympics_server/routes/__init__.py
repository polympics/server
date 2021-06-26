"""Load the API routes and expose the application."""
from . import (              # noqa:F401
    accounts,
    auth,
    awards,
    callbacks,
    contests,
    teams
)
from .utils import server    # noqa:F401
