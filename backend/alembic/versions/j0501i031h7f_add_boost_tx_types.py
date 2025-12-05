"""add boost tx types to enum

Revision ID: j0501i031h7f
Revises: i9400h920g6e
Create Date: 2025-12-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'j0501i031h7f'
down_revision: Union[str, Sequence[str], None] = 'i9400h920g6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to txtype enum for boost system
    op.execute("ALTER TYPE txtype ADD VALUE IF NOT EXISTS 'boost_purchase'")
    op.execute("ALTER TYPE txtype ADD VALUE IF NOT EXISTS 'auto_claim_commission'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # Would need to recreate the enum type
    pass
