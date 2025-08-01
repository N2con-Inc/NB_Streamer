"""Authentication service for NB_Streamer."""

import base64
import secrets
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param

from ..config import config


class AuthService:
    """Handle authentication for incoming requests."""

    def __init__(self):
        self.auth_type = config.auth_type
        self.bearer_security = (
            HTTPBearer(auto_error=False) if self.auth_type == "bearer" else None
        )
        self.basic_security = (
            HTTPBasic(auto_error=False) if self.auth_type == "basic" else None
        )

    async def authenticate(self, request: Request) -> bool:
        """
        Authenticate incoming request based on configured auth type.

        Args:
            request: FastAPI request object

        Returns:
            bool: True if authentication successful

        Raises:
            HTTPException: If authentication fails
        """
        if self.auth_type == "none":
            return True

        try:
            if self.auth_type == "bearer":
                return await self._authenticate_bearer(request)
            elif self.auth_type == "basic":
                return await self._authenticate_basic(request)
            elif self.auth_type == "header":
                return await self._authenticate_header(request)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unsupported auth type: {self.auth_type}",
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}",
            )

    async def _authenticate_bearer(self, request: Request) -> bool:
        """Authenticate using Bearer token."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not token or not self._secure_compare(token, config.auth_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return True

    async def _authenticate_basic(self, request: Request) -> bool:
        """Authenticate using Basic authentication."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Basic"},
            )

        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme.lower() != "basic":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Basic"},
            )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        try:
            decoded = base64.b64decode(credentials).decode("utf-8")
            username, password = decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials format",
                headers={"WWW-Authenticate": "Basic"},
            )

        if not (
            self._secure_compare(username, config.auth_username)
            and self._secure_compare(password, config.auth_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        return True

    async def _authenticate_header(self, request: Request) -> bool:
        """Authenticate using custom header."""
        header_value = request.headers.get(config.auth_header_name)
        if not header_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Header '{config.auth_header_name}' required",
            )

        if not self._secure_compare(header_value, config.auth_header_value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid header value"
            )

        return True

    def _secure_compare(self, a: Optional[str], b: Optional[str]) -> bool:
        """Securely compare two strings to prevent timing attacks."""
        if a is None or b is None:
            return False
        return secrets.compare_digest(a.encode(), b.encode())
