"""
Auth Router - Registration, login, token refresh, and logout endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.config import settings
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, TokenRefresh
from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_user_by_id,
    EmailAlreadyExistsError,
    AuthenticationError,
)
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    store_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
)
from app.utils.dependencies import CurrentUser


router = APIRouter(tags=["Authentication"])


# Request/Response Models specific to auth endpoints
class LoginRequest(BaseModel):
    """Email/password login request."""
    
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=1, examples=["SecureP@ss123"])


class AuthResponse(BaseModel):
    """Response containing user data and tokens."""
    
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=settings.access_token_expire_minutes * 60,
        description="Access token expiration in seconds"
    )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str


# Helper function to generate tokens
def _create_tokens(user) -> tuple[str, str]:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        is_admin=user.is_admin
    )
    refresh_token = create_refresh_token(user_id=user.id)
    
    # Store refresh token in Redis for revocation tracking
    store_refresh_token(refresh_token, user.id)
    
    return access_token, refresh_token


# Endpoints
@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens."
)
async def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)]
) -> AuthResponse:
    """
    Register a new user with email and password.
    
    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters with letter and number
    - **name**: User's display name (2-100 characters)
    - **phone**: Optional phone number
    - **date_of_birth**: Optional date (must be 18+)
    - **gender**: Optional (male/female/other/prefer_not_to_say)
    
    Returns user data and authentication tokens on success.
    """
    try:
        user = register_user(db, user_data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    access_token, refresh_token = _create_tokens(user)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate with email and password to receive tokens."
)
async def login(
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
) -> AuthResponse:
    """
    Authenticate user with email and password.
    
    Returns user data and authentication tokens on success.
    Updates last_login_at timestamp.
    """
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, refresh_token = _create_tokens(user)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/login/form",
    response_model=Token,
    summary="OAuth2 password login",
    description="OAuth2-compatible login endpoint for Swagger UI.",
    include_in_schema=False  # Hide from docs, used by OAuth2PasswordBearer
)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """
    OAuth2 password flow login (used by Swagger UI's Authorize button).
    Accepts form data with username (email) and password.
    """
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, refresh_token = _create_tokens(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token."
)
async def refresh_token(
    token_request: TokenRefresh,
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """
    Get a new access token using a valid refresh token.
    
    The refresh token must:
    - Be a valid JWT
    - Not be expired
    - Not be revoked (exist in Redis)
    
    Returns a new access token. The refresh token remains valid.
    """
    # Decode the refresh token
    user_id = decode_refresh_token(token_request.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is revoked
    if not is_refresh_token_valid(token_request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create new access token only
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        is_admin=user.is_admin
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Revoke the current refresh token."
)
async def logout(
    token_request: TokenRefresh,
    current_user: CurrentUser
) -> MessageResponse:
    """
    Logout by revoking the provided refresh token.
    
    Requires a valid access token in the Authorization header.
    The refresh token will be removed from Redis.
    """
    # Verify the refresh token belongs to the current user
    user_id = decode_refresh_token(token_request.refresh_token)
    
    if user_id is None or user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    # Revoke the token
    revoke_refresh_token(token_request.refresh_token)
    
    return MessageResponse(message="Successfully logged out")

