"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    Upgrade database schema (apply this migration).
    
    This function is called when you run: alembic upgrade head
    It contains the forward migration logic (e.g., CREATE TABLE, ADD COLUMN).
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Downgrade database schema (revert this migration).
    
    This function is called when you run: alembic downgrade -1
    It contains the rollback logic (e.g., DROP TABLE, DROP COLUMN).
    
    IMPORTANT: Always implement downgrade to allow reverting changes!
    """
    ${downgrades if downgrades else "pass"}

