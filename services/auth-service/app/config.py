"""
Configuration Management using Pydantic Settings

This module handles all configuration and environment variables for the auth service.
It uses Pydantic's BaseSettings which automatically:
1. Loads values from environment variables
2. Validates data types
3. Provides default values
4. Raises errors if required settings are missing

Environment variables can come from:
- .env file (for local development)
- Docker environment (docker-compose.yml)
- System environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings
    
    All settings are loaded from environment variables.
    See .env.example for a full list of available settings.
    """
    
    # ============================================
    # Application Settings
    # ============================================
    app_name: str = "RideMatch Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False  # Set to True in development for detailed error messages
    
    # ============================================
    # Database Settings (PostgreSQL)
    # ============================================
    # These settings construct the database connection URL
    # Format: postgresql://username:password@host:port/database
    
    database_host: str = "auth-db"  # Container name in docker-compose
    database_port: int = 5432
    database_name: str = "auth_db"
    database_user: str = "postgres"
    database_password: str = "postgres"
    
    @property
    def database_url(self) -> str:
        """
        Constructs the full database connection URL
        
        Returns:
            str: PostgreSQL connection string
            Example: postgresql://postgres:postgres@auth-db:5432/auth_db
        """
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
    
    # ============================================
    # Redis Settings (Cache & Sessions)
    # ============================================
    redis_host: str = "redis"  # Container name in docker-compose
    redis_port: int = 6379
    redis_db: int = 0  # Redis has 16 databases (0-15), we use 0 for auth service
    redis_password: Optional[str] = None  # Optional password for Redis
    
    @property
    def redis_url(self) -> str:
        """
        Constructs the full Redis connection URL
        
        Returns:
            str: Redis connection string
            Example: redis://:password@redis:6379/0 or redis://redis:6379/0
        """
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ============================================
    # JWT (JSON Web Token) Settings
    # ============================================
    # JWT tokens are used for authentication
    # The secret key MUST be kept secure and should be a long random string
    
    jwt_secret_key: str = "your-secret-key-change-this-in-production"  # MUST change in production!
    jwt_algorithm: str = "HS256"  # Algorithm for signing tokens (HS256 is standard)
    
    # Token expiration times (in minutes)
    access_token_expire_minutes: int = 15  # Short-lived access token (15 minutes)
    refresh_token_expire_minutes: int = 10080  # Long-lived refresh token (7 days = 7*24*60)
    
    # ============================================
    # CORS (Cross-Origin Resource Sharing) Settings
    # ============================================
    # CORS allows the frontend (running on different domain) to call our API
    # In production, specify exact frontend URLs instead of "*"
    
    cors_origins: list[str] = [
        "http://localhost:3000",  # React development server
        "http://localhost",       # Nginx gateway
        "http://127.0.0.1:3000",
    ]
    
    # ============================================
    # Security Settings
    # ============================================
    # Password hashing configuration
    # bcrypt is a secure hashing algorithm
    bcrypt_rounds: int = 12  # Higher = more secure but slower (12 is good balance)
    
    # ============================================
    # API Settings
    # ============================================
    api_prefix: str = "/api/auth"  # All endpoints will be prefixed with this
    
    # ============================================
    # Pagination Settings
    # ============================================
    # Default values for paginated endpoints
    default_page_size: int = 20
    max_page_size: int = 100
    
    # ============================================
    # Pydantic Configuration
    # ============================================
    model_config = SettingsConfigDict(
        # Load environment variables from .env file (for local development)
        env_file=".env",
        # Allow .env file to not exist (useful in production with real env vars)
        env_file_encoding="utf-8",
        # Make settings case-insensitive (DATABASE_HOST = database_host)
        case_sensitive=False,
        # Allow extra fields (forward compatibility)
        extra="ignore",
    )


# ============================================
# Create Global Settings Instance
# ============================================
# This creates a single instance of Settings that's used throughout the app
# It automatically loads all environment variables when imported

settings = Settings()


# ============================================
# Usage Example
# ============================================
"""
To use these settings in your code:

from app.config import settings

# Access database URL
db_url = settings.database_url

# Access JWT settings
secret = settings.jwt_secret_key
expire = settings.access_token_expire_minutes

# Check if debug mode
if settings.debug:
    print("Running in debug mode!")
"""

