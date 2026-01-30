"""FastAPI dependencies."""

from .database import get_db
from .auth import get_current_user, require_scope

__all__ = ["get_db", "get_current_user", "require_scope"]
