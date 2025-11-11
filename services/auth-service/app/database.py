"""
Database Configuration and Session Management

This module handles PostgreSQL and Redis connections for the auth service.
- SQLAlchemy engine: Connection pool management
- SessionLocal: Session factory for database transactions
- Base: Foundation class for all ORM models
- Redis client: Caching and session storage
- FastAPI dependencies: Automatic session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import redis
from app.config import settings


# ============================================
# PostgreSQL Setup
# ============================================

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,  # postgresql://user:pass@host:port/db
    pool_pre_ping=True,     # Test connections before use (prevents stale connections)
    echo=settings.debug,    # Log SQL queries in debug mode
    pool_size=5,           # Keep 5 connections in pool
    max_overflow=10,       # Allow 10 additional connections (total 15 max)
)

# Create session factory
# Sessions manage transactions and track changes
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control
    autoflush=False,   # Manual flush control
    bind=engine
)

# Base class for all ORM models
# All models inherit from this: class User(Base)
Base = declarative_base()


# ============================================
# Redis Setup
# ============================================

# Redis client for caching, sessions, and refresh tokens
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True,  # Convert bytes to strings
    socket_connect_timeout=5,
    socket_timeout=5,
)


# ============================================
# FastAPI Dependencies
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Provides database session for each request.
    Automatically handles session creation and cleanup.
    
    Usage:
        @router.post("/register")
        def register(db: Session = Depends(get_db)):
            db.add(new_user)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """
    Provides Redis client for caching and session management.
    
    Usage:
        @router.get("/data")
        def get_data(cache: redis.Redis = Depends(get_redis)):
            return cache.get("key")
    """
    return redis_client


# ============================================
# Utility Functions
# ============================================

def test_db_connection() -> bool:
    """Test PostgreSQL connection. Returns True if successful."""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_redis_connection() -> bool:
    """Test Redis connection. Returns True if successful."""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False
