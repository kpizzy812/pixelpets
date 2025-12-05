"""update pet prices and add crystal turtle

Revision ID: f6277f607d3b
Revises: c1234567890a
Create Date: 2025-12-05 14:08:25.071537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6277f607d3b'
down_revision: Union[str, Sequence[str], None] = 'c1234567890a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update Robo-Bunny: 150 -> 250
    op.execute("""
        UPDATE pet_types
        SET base_price = 250,
            level_prices = '{"BABY": 250, "ADULT": 1000, "MYTHIC": 2500}'
        WHERE name = 'Robo-Bunny'
    """)

    # Update Ember Dragon: 300 -> 1000
    op.execute("""
        UPDATE pet_types
        SET base_price = 1000,
            level_prices = '{"BABY": 1000, "ADULT": 4000, "MYTHIC": 10000}'
        WHERE name = 'Ember Dragon'
    """)

    # Add Crystal Turtle (only if not exists)
    op.execute("""
        INSERT INTO pet_types (name, emoji, image_key, base_price, daily_rate, roi_cap_multiplier, level_prices, is_active, created_at)
        SELECT 'Crystal Turtle', '🐢', 'turtle', 500, 0.022, 1.9, '{"BABY": 500, "ADULT": 2000, "MYTHIC": 5000}', true, NOW()
        WHERE NOT EXISTS (SELECT 1 FROM pet_types WHERE name = 'Crystal Turtle')
    """)


def downgrade() -> None:
    # Revert Robo-Bunny
    op.execute("""
        UPDATE pet_types
        SET base_price = 150,
            level_prices = '{"BABY": 150, "ADULT": 600, "MYTHIC": 1500}'
        WHERE name = 'Robo-Bunny'
    """)

    # Revert Ember Dragon
    op.execute("""
        UPDATE pet_types
        SET base_price = 300,
            level_prices = '{"BABY": 300, "ADULT": 1200, "MYTHIC": 3000}'
        WHERE name = 'Ember Dragon'
    """)

    # Remove Crystal Turtle
    op.execute("DELETE FROM pet_types WHERE name = 'Crystal Turtle'")
