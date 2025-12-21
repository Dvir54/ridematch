"""
Auth Service - User registration, authentication, and profile management.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.password import hash_password, verify_password


class EmailAlreadyExistsError(Exception):
    """Email already registered."""
    pass


class AuthenticationError(Exception):
    """Invalid credentials or inactive account."""
    pass


def email_exists(db: Session, email: str) -> bool:
    """Check if email is already registered."""
    return db.query(User).filter(User.email == email).first() is not None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user. Raises EmailAlreadyExistsError if email taken."""
    if email_exists(db, user_data.email):
        raise EmailAlreadyExistsError(f"Email '{user_data.email}' is already registered")
    
    db_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "users_email_key" in str(e.orig) or "unique constraint" in str(e.orig).lower():
            raise EmailAlreadyExistsError(f"Email '{user_data.email}' is already registered")
        raise


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user. Raises AuthenticationError on failure."""
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise AuthenticationError("Invalid email or password")
    
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


def update_user_profile(db: Session, user: User, update_data: UserUpdate) -> User:
    """Update user profile with provided fields."""
    for field, value in update_data.get_update_dict().items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user
