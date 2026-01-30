"""Error handling middleware."""

from datetime import datetime
from typing import Union
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


class ErrorResponse:
    """Standard error response format (RFC 7807 Problem Details)."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Union[dict, None] = None,
        request_id: str = None
    ):
        self.error = {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id or str(uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def to_dict(self):
        return self.error


def add_error_handlers(app: FastAPI):
    """Add error handlers to FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors (400)."""
        error_details = {}
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"])
            error_details[field] = error["msg"]

        error_response = ErrorResponse(
            code="INVALID_REQUEST",
            message="Request validation failed",
            details=error_details
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.to_dict()
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (409)."""
        error_response = ErrorResponse(
            code="CONFLICT",
            message="Resource already exists or constraint violation",
            details={"database_error": str(exc.orig)}
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response.to_dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors (500)."""
        error_response = ErrorResponse(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(exc)}
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict()
        )
