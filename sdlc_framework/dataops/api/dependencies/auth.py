"""Authentication and authorization dependencies."""

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


# HTTP Bearer token security
security = HTTPBearer()


class User(BaseModel):
    """Authenticated user information."""
    user_id: UUID
    client_id: UUID
    scopes: List[str]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from bearer token.

    In production, this would:
    1. Validate JWT token signature
    2. Check token expiration
    3. Extract user claims (user_id, client_id, scopes)
    4. Return User object

    For demo purposes, we'll accept any token and return a mock user.
    """
    token = credentials.credentials

    # TODO: Implement real JWT validation
    # For now, return a mock user
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Mock user (in production, extract from JWT)
    return User(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),
        client_id=UUID("00000000-0000-0000-0000-000000000002"),
        scopes=["dataops:datasets:read", "dataops:datasets:write", "dataops:templates:read"]
    )


def require_scope(required_scope: str):
    """Dependency to require specific scope.

    Usage:
        @router.get("/datasets", dependencies=[Depends(require_scope("dataops:datasets:read"))])
    """
    async def scope_checker(user: User = Depends(get_current_user)) -> User:
        if required_scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}"
            )
        return user

    return scope_checker
