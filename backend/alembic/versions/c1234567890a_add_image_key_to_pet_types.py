"""add image_key to pet_types

Revision ID: c1234567890a
Revises: a446f8a359bc
Create Date: 2025-12-05 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1234567890a'
down_revision: Union[str, Sequence[str], None] = 'a446f8a359bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Mapping of pet type names to image keys
PET_IMAGE_KEYS = {
    'Bubble Slime': 'bubble',
    'Pixel Fox': 'fox',
    'Glitch Cat': 'cat',
    'Robo-Bunny': 'rabbit',
    'Ember Dragon': 'dragon',
}


def upgrade() -> None:
    """Add image_key column to pet_types."""
    # Add column as nullable first
    op.add_column('pet_types', sa.Column('image_key', sa.String(length=50), nullable=True))

    # Update existing rows with image_key values based on pet name
    for name, image_key in PET_IMAGE_KEYS.items():
        op.execute(
            f"UPDATE pet_types SET image_key = '{image_key}' WHERE name = '{name}'"
        )

    # Make column NOT NULL after data is populated
    op.alter_column('pet_types', 'image_key', nullable=False)


def downgrade() -> None:
    """Remove image_key column from pet_types."""
    op.drop_column('pet_types', 'image_key')
