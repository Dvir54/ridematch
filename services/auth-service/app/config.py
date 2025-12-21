"""
Configuration Management

Loads settings from environment variables with validation and defaults.
Uses Pydantic BaseSettings for automatic env var loading from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "RideMatch Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database (PostgreSQL)
    database_host: str = "auth-db"
    database_port: int = 5432
    database_name: str = "auth_db"
    database_user: str = "postgres"
    database_password: str = "postgres"
    
    @property
    def database_url(self) -> str:
        """PostgreSQL connection string."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
    
    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    @property
    def redis_url(self) -> str:
        """Redis connection string."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15      # 15 minutes
    refresh_token_expire_minutes: int = 10080  # 7 days
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost",
        "http://127.0.0.1:3000",
    ]
    
    # Security
    bcrypt_rounds: int = 12
    
    # API
    api_prefix: str = "/api/auth"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
