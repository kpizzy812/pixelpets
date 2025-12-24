"""add_is_available_to_pet_types

Revision ID: l2703k253j9h
Revises: k1602j142i8g
Create Date: 2025-12-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'l2703k253j9h'
down_revision: Union[str, Sequence[str], None] = 'k1602j142i8g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_available column to pet_types table."""
    op.add_column('pet_types', sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    """Remove is_available column from pet_types table."""
    op.drop_column('pet_types', 'is_available')
