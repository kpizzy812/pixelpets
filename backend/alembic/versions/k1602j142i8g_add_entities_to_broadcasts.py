"""add_entities_to_broadcasts

Revision ID: k1602j142i8g
Revises: 05dc671d7118
Create Date: 2025-12-07 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'k1602j142i8g'
down_revision: Union[str, Sequence[str], None] = '05dc671d7118'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add entities column to broadcasts table."""
    op.add_column('broadcasts', sa.Column('entities', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove entities column from broadcasts table."""
    op.drop_column('broadcasts', 'entities')
