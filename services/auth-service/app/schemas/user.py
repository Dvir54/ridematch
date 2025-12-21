"""
User Schemas - Request/Response validation for user endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, date

from app.utils.dates import calculate_age


# Validation Helpers
def _validate_name(v: str) -> str:
    """Strip whitespace and reject empty names."""
    stripped = v.strip()
    if not stripped:
        raise ValueError("Name cannot be empty or only whitespace")
    return stripped


def _validate_gender(v: str) -> str:
    """Validate and normalize gender value."""
    allowed = {"male", "female", "other", "prefer_not_to_say"}
    if v.lower() not in allowed:
        raise ValueError(f"Gender must be one of: {', '.join(allowed)}")
    return v.lower()


def _validate_date_of_birth(v: date) -> date:
    """Validate date of birth: not future, 18+, within 100 years."""
    today = date.today()
    if v > today:
        raise ValueError("Date of birth cannot be in the future")
    
    age = calculate_age(v)
    if age < 18:
        raise ValueError("Users must be at least 18 years old")
    if age > 100:
        raise ValueError("Invalid date of birth")
    
    return v


def _validate_preferences(v: dict) -> dict:
    """Validate preferences structure and values."""
    if "default_mode" in v and v["default_mode"] not in ("driver", "passenger"):
        raise ValueError("default_mode must be 'driver' or 'passenger'")
    
    for field in ["smoking", "pets"]:
        if field in v and not isinstance(v[field], bool):
            raise ValueError(f"{field} must be a boolean")
    
    if "notifications" in v:
        notif = v["notifications"]
        if not isinstance(notif, dict):
            raise ValueError("notifications must be an object")
        for field in ["email", "push", "websocket"]:
            if field in notif and not isinstance(notif[field], bool):
                raise ValueError(f"notifications.{field} must be a boolean")
    
    if "language" in v and v["language"] not in ("en", "he"):
        raise ValueError("language must be 'en' or 'he'")
    
    if "theme" in v and v["theme"] not in ("light", "dark"):
        raise ValueError("theme must be 'light' or 'dark'")
    
    return v


def _validate_password(v: str) -> str:
    """Validate password contains letter and number."""
    if not any(char.isalpha() for char in v):
        raise ValueError("Password must contain at least one letter")
    if not any(char.isdigit() for char in v):
        raise ValueError("Password must contain at least one number")
    return v


# Schemas
class UserBase(BaseModel):
    """Common fields shared by user schemas."""
    
    email: EmailStr = Field(..., examples=["user@example.com"])
    name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_name(v)

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    """Registration request schema."""
    
    password: str = Field(..., min_length=8, max_length=128, examples=["SecureP@ss123"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+972-52-1234567"])
    date_of_birth: Optional[date] = Field(None, examples=["1990-05-15"])
    gender: Optional[str] = Field(None, examples=["male", "female", "other"])
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        return _validate_gender(v) if v else v
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        return _validate_date_of_birth(v) if v else v


class UserResponse(UserBase):
    """User API response (excludes password)."""
    
    id: int
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True
    is_email_verified: bool = False
    driver_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    driver_rating_count: int = 0
    passenger_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    passenger_rating_count: int = 0
    preferences: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Profile update request (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    preferences: Optional[dict] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return _validate_name(v) if v else v
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        return _validate_gender(v) if v else v
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        return _validate_date_of_birth(v) if v else v
    
    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v: Optional[dict]) -> Optional[dict]:
        return _validate_preferences(v) if v else v
    
    def get_update_dict(self) -> dict:
        """Return only fields that were explicitly set."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class UserPublic(BaseModel):
    """Public profile visible to other users (minimal info)."""
    
    id: int
    name: str
    driver_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    driver_rating_count: int = 0
    passenger_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    passenger_rating_count: int = 0

    model_config = {"from_attributes": True}
