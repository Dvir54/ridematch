"""Create users table with full schema

Revision ID: 001_create_users
Revises: 
Create Date: 2025-11-21

This migration creates the users table with all necessary columns for:
- Authentication (email, password, admin flag)
- Profile information (name, phone, gender, date of birth)
- Account status (active, email verification)
- Cached ratings (driver and passenger ratings)
- Timestamps (created, updated, last login)
- Preferences (JSON field for user settings)

Design Decision:
- No static 'role' column - users can be both driver and passenger
- is_admin flag for admin access only
- Ratings cached from feedback-service for performance
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_create_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the users table with all columns, indexes, and constraints
    """
    # Create users table
    op.create_table(
        'users',
        
        # ========================================
        # Core Identity & Authentication
        # ========================================
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Unique user identifier'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='User email address for login'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='Bcrypt hashed password'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false', comment='Admin access flag'),
        
        # ========================================
        # Profile Information
        # ========================================
        sa.Column('name', sa.String(length=100), nullable=False, comment='User full name'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Phone number for contact'),
        sa.Column('date_of_birth', sa.Date(), nullable=True, comment='Date of birth for age verification (18+)'),
        sa.Column('gender', sa.String(length=20), nullable=True, comment='Gender: male, female, other, prefer_not_to_say'),
        
        # ========================================
        # Account Status & Verification
        # ========================================
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Account active status'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false', comment='Email verification status'),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True, comment='Email verification timestamp'),
        
        # ========================================
        # Cached Ratings (Performance Optimization)
        # ========================================
        sa.Column('driver_rating', sa.Float(), nullable=True, comment='Average rating as driver (1.0-5.0)'),
        sa.Column('driver_rating_count', sa.Integer(), nullable=False, server_default='0', comment='Number of ratings as driver'),
        sa.Column('passenger_rating', sa.Float(), nullable=True, comment='Average rating as passenger (1.0-5.0)'),
        sa.Column('passenger_rating_count', sa.Integer(), nullable=False, server_default='0', comment='Number of ratings as passenger'),
        
        # ========================================
        # Timestamps
        # ========================================
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Account creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='Last login timestamp'),
        
        # ========================================
        # Preferences (JSON)
        # ========================================
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='User preferences and settings'),
        
        # ========================================
        # Constraints
        # ========================================
        sa.PrimaryKeyConstraint('id', name='users_pkey'),
        sa.UniqueConstraint('email', name='users_email_key')
    )
    
    # ========================================
    # Indexes for Performance
    # ========================================
    
    # Index on id (primary key automatically indexed, but explicit for clarity)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    
    # Index on email for fast login lookups
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Index on is_active for filtering active users
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    
    # Composite index for admin queries
    op.create_index('ix_users_is_admin_is_active', 'users', ['is_admin', 'is_active'], unique=False)
    
    print("✅ Created users table with 18 columns and indexes")


def downgrade() -> None:
    """
    Drop the users table and all indexes
    """
    # Drop indexes first
    op.drop_index('ix_users_is_admin_is_active', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    print("✅ Dropped users table and indexes")

