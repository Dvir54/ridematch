"""
User Model - SQLAlchemy ORM

Represents the users table. Users can act as both drivers and passengers.
Role is contextual (determined by action), not stored. Only admin status is stored.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Date, JSON
from sqlalchemy.sql import func
from app.database import Base
from app.utils.dates import calculate_age


class User(Base):
    """User model - can be both driver and passenger."""
    
    __tablename__ = "users"
    
    # Core Identity
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Profile
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other, prefer_not_to_say
    
    # Account Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cached Ratings (synced from feedback-service)
    driver_rating = Column(Float, nullable=True, default=None)
    driver_rating_count = Column(Integer, default=0, nullable=False)
    passenger_rating = Column(Float, nullable=True, default=None)
    passenger_rating_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences (JSON: default_mode, smoking, pets, notifications, language, theme)
    preferences = Column(JSON, nullable=True, default=dict)
    
    def __repr__(self):
        admin_flag = " [ADMIN]" if self.is_admin else ""
        verified_flag = " [VERIFIED]" if self.is_email_verified else ""
        return f"<User(id={self.id}, email='{self.email}'{admin_flag}{verified_flag})>"
    
    @property
    def age(self) -> int | None:
        """Calculate current age from date_of_birth."""
        if not self.date_of_birth:
            return None
        return calculate_age(self.date_of_birth)
    
    @property
    def is_adult(self) -> bool | None:
        """Check if user is 18+ years old."""
        if not self.age:
            return None
        return self.age >= 18
    
    def get_default_mode(self) -> str:
        """Get preferred UI mode: 'driver' or 'passenger'."""
        if self.preferences and isinstance(self.preferences, dict):
            return self.preferences.get("default_mode", "passenger")
        return "passenger"
    
    def update_rating(self, role: str, new_rating: float):
        """Update cached rating when new feedback is submitted."""
        if role == "driver":
            if self.driver_rating is None:
                self.driver_rating = new_rating
                self.driver_rating_count = 1
            else:
                total = self.driver_rating * self.driver_rating_count + new_rating
                self.driver_rating_count += 1
                self.driver_rating = total / self.driver_rating_count
                
        elif role == "passenger":
            if self.passenger_rating is None:
                self.passenger_rating = new_rating
                self.passenger_rating_count = 1
            else:
                total = self.passenger_rating * self.passenger_rating_count + new_rating
                self.passenger_rating_count += 1
                self.passenger_rating = total / self.passenger_rating_count
