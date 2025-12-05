"""merge boost and other migrations

Revision ID: 53e61c719b14
Revises: 958018a7a883, j0501i031h7f
Create Date: 2025-12-06 00:45:56.595288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53e61c719b14'
down_revision: Union[str, Sequence[str], None] = ('958018a7a883', 'j0501i031h7f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
