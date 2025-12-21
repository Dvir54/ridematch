"""
Date Utilities
"""

from datetime import date


def calculate_age(date_of_birth: date) -> int:
    """Calculate age in years from date of birth."""
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def is_adult(date_of_birth: date, min_age: int = 18) -> bool:
    """Check if person is at least min_age years old."""
    return calculate_age(date_of_birth) >= min_age
