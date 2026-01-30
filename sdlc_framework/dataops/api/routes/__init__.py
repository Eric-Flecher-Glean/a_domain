"""API route handlers."""

from .datasets import router as datasets_router
from .templates import router as templates_router
from .health import router as health_router

__all__ = ["datasets_router", "templates_router", "health_router"]
