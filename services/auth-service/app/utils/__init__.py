"""
Utility Functions and Helpers

Reusable utilities for password hashing and date calculations.

Note: Dependencies (get_current_user, etc.) are NOT imported here to avoid
circular imports with app.models.user. Import them directly:
    from app.utils.dependencies import get_current_user, CurrentUser, etc.
"""

from app.utils.dates import calculate_age, is_adult
from app.utils.password import hash_password, verify_password

__all__ = [
    "calculate_age",
    "is_adult",
    "hash_password",
    "verify_password",
]
