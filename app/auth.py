"""Bearer token authentication for the MCP server"""
import os
import secrets
from typing import Optional

class AuthError(Exception):
    """Raised when authentication fails"""
    pass

def get_expected_token() -> str:
    """Load auth token from environment. Fail loudly if missing"""
    token = os.getenv("MCP_AUTH_TOKEN")
    if not token:
        raise RuntimeError(
            "MCP_AUTH_TOKEN env var not set"
            "Generate one with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )
    if len(token) < 32:
        raise RuntimeError("The token must be at least 32 characters")
    return token

def verify_bearer_token(authorization_header: Optional[str]) -> None:
    """
    Validate the Authorization Header against the expected token
    Uses constant-time comparison to prevent timing attacks
    """

    expected = get_expected_token()

    if not authorization_header:
        raise AuthError("Missing authorization header")
    
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower != "bearer":
        raise AuthError("The authorization header format must be: Bearer <token>")
    
    provided = parts[1]

    if not secrets.compare_digest(provided, expected):
        raise AuthError("Invalid Bearer Token")