"""Add progress-based task types to enum

Revision ID: m3804l364k0i
Revises: l2703k253j9h
Create Date: 2024-12-24 05:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'm3804l364k0i'
down_revision: Union[str, None] = 'l2703k253j9h'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to tasktype enum
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'OTHER'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'INVITE_FRIEND'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'INVITE_ACTIVE_FRIEND'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'BUY_PET'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # Would need to recreate the type
    pass
