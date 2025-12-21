"""
Alembic Migration Environment

This file is run whenever you execute an Alembic command (upgrade, downgrade, revision, etc.)
It configures:
1. How to connect to the database
2. Which models to track for changes
3. How to run migrations (online vs offline mode)
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import our application's configuration
from app.config import settings

# Import the Base class from our database module
# This is CRITICAL! Base.metadata contains all our models
# Without this import, Alembic won't see any models
from app.database import Base

# Import all models here so Alembic can detect them
# When you create new models, import them here!
from app.models import User  # Import User model for detection


# ============================================
# Alembic Configuration
# ============================================

# This is the Alembic Config object
# It provides access to values in alembic.ini
config = context.config

# Set the database URL from our application settings
# This allows us to use environment variables instead of hardcoding in alembic.ini
# config.set_main_option() updates the configuration at runtime
config.set_main_option("sqlalchemy.url", settings.database_url)

# Setup Python logging from alembic.ini [loggers] section
# This enables logging for migration operations
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to Base.metadata
# This tells Alembic which tables to track
# Base.metadata contains all models that inherit from Base
# Example: If you have User(Base), Ride(Base), Base.metadata knows about both
target_metadata = Base.metadata


# ============================================
# Migration Functions
# ============================================

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    Offline mode doesn't connect to the database.
    Instead, it generates SQL statements to a file.
    
    Usage:
        alembic upgrade head --sql > migration.sql
    
    This is useful for:
    - Reviewing SQL before running it
    - Running migrations manually on production
    - Database administrators who want to review changes
    
    How it works:
    1. Gets database URL from config
    2. Creates a context with that URL (no actual connection)
    3. Runs migrations, outputting SQL statements
    """
    url = config.get_main_option("sqlalchemy.url")
    
    # Configure the context with just the URL (no engine needed)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Generate SQL with actual values instead of parameters
        dialect_opts={"paramstyle": "named"},  # Use named parameters (:param_name)
    )

    # Run migrations in a transaction
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    Online mode connects to the database and executes migrations directly.
    This is the normal mode used during development and deployment.
    
    Usage:
        alembic upgrade head
    
    How it works:
    1. Creates a database engine from configuration
    2. Connects to the database
    3. Executes migration SQL statements
    4. Updates alembic_version table to track current version
    
    Connection Pooling:
    - Uses NullPool (no connection pooling for migrations)
    - Migrations are one-time operations, don't need persistent connections
    - Prevents connection exhaustion issues
    """
    # Create an Engine from alembic.ini configuration
    # engine_from_config() reads [alembic] section and creates SQLAlchemy engine
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No connection pooling for migrations
    )

    # Connect to the database
    with connectable.connect() as connection:
        # Configure migration context with the active connection
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Optional: compare_type=True to detect column type changes
            # compare_type=True,
            # Optional: compare_server_default=True to detect default value changes
            # compare_server_default=True,
        )

        # Run migrations within a transaction
        # If any migration fails, everything is rolled back
        with context.begin_transaction():
            context.run_migrations()


# ============================================
# Entry Point
# ============================================

# Determine which mode to run in
# context.is_offline_mode() returns True if --sql flag is used
if context.is_offline_mode():
    # Generate SQL to file (no database connection)
    run_migrations_offline()
else:
    # Execute migrations directly on database (default)
    run_migrations_online()

