"""
Database Configuration

PostgreSQL and Redis connection setup with session management.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import redis
from app.config import settings


# PostgreSQL
engine = create_engine(
    settings.database_url,  # postgresql://user:pass@host:port/db
    pool_pre_ping=True,     # Test connections before use (prevents stale connections)
    echo=settings.debug,    # Log SQL queries in debug mode
    pool_size=5,           # Keep 5 connections in pool
    max_overflow=10,       # Allow 10 additional connections (total 15 max)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Redis
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True,  # Convert bytes to strings
    socket_connect_timeout=5,
    socket_timeout=5,
)


# FastAPI Dependencies
def get_db() -> Generator[Session, None, None]:
    """Provide database session per request with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """Provide Redis client for caching."""
    return redis_client


# Connection Tests
def test_db_connection() -> bool:
    """Test PostgreSQL connection."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def test_redis_connection() -> bool:
    """Test Redis connection."""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
