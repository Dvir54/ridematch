"""
Business Logic Layer

Service modules contain core business logic for authentication and user management.
"""

from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    store_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
    revoke_all_user_tokens,
)

from app.services.auth_service import (
    register_user,
    EmailAlreadyExistsError,
    authenticate_user,
    AuthenticationError,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    email_exists,
)

__all__ = [
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "store_refresh_token",
    "is_refresh_token_valid",
    "revoke_refresh_token",
    "revoke_all_user_tokens",
    # Auth
    "register_user",
    "EmailAlreadyExistsError",
    "authenticate_user",
    "AuthenticationError",
    "get_user_by_email",
    "get_user_by_id",
    "update_user_profile",
    "email_exists",
]
