"""
Token Schemas - JWT token request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """Token response after successful login/register."""
    
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."])
    token_type: str = Field(default="bearer")
    refresh_token: Optional[str] = Field(None, examples=["eyJhbGciOiJIUzI1NiIs..."])
    expires_in: Optional[int] = Field(None, examples=[900])  # seconds


class TokenData(BaseModel):
    """Data decoded from JWT payload (internal use)."""
    
    user_id: Optional[int] = None
    email: Optional[str] = None
    is_admin: bool = False
    token_type: Optional[str] = "access"


class TokenRefresh(BaseModel):
    """Refresh token request."""
    
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."])
