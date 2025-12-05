"""add spin tx types to enum

Revision ID: i9400h920g6e
Revises: h8399g819f5d
Create Date: 2025-12-05 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'i9400h920g6e'
down_revision: Union[str, Sequence[str], None] = 'h8399g819f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to txtype enum
    op.execute("ALTER TYPE txtype ADD VALUE IF NOT EXISTS 'SPIN_COST'")
    op.execute("ALTER TYPE txtype ADD VALUE IF NOT EXISTS 'SPIN_WIN'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # Would need to recreate the enum type
    pass
