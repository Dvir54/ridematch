"""
Users Router - User profile and lookup endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserResponse, UserUpdate, UserPublic
from app.services.auth_service import get_user_by_id, update_user_profile
from app.utils.dependencies import ActiveUser, DbSession


router = APIRouter(tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_me(current_user: ActiveUser) -> UserResponse:
    """Return the authenticated user's full profile."""
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile"
)
async def update_me(
    update_data: UserUpdate,
    current_user: ActiveUser,
    db: DbSession
) -> UserResponse:
    """Update the authenticated user's profile."""
    updated_user = update_user_profile(db, current_user, update_data)
    return UserResponse.model_validate(updated_user)


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get user by ID"
)
async def get_user(
    user_id: int,
    current_user: ActiveUser,
    db: DbSession
) -> UserPublic:
    """Return basic public profile of a user."""
    user = get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)

