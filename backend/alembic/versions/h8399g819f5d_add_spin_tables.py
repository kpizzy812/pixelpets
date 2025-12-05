"""add spin tables

Revision ID: h8399g819f5d
Revises: g7288f708e4c
Create Date: 2025-12-05 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8399g819f5d'
down_revision: Union[str, Sequence[str], None] = 'g7288f708e4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create spin_rewards table
    op.create_table('spin_rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.Enum('XPET', 'NOTHING', 'BONUS_PERCENT', name='spinrewardtype'), nullable=False),
        sa.Column('value', sa.Numeric(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('emoji', sa.String(length=10), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=False),
        sa.Column('probability', sa.Numeric(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_spins table
    op.create_table('user_spins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reward_id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.Enum('XPET', 'NOTHING', 'BONUS_PERCENT', name='spinrewardtype', create_type=False), nullable=False),
        sa.Column('reward_value', sa.Numeric(), nullable=False),
        sa.Column('cost_xpet', sa.Numeric(), nullable=False, default=0),
        sa.Column('is_free_spin', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reward_id'], ['spin_rewards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_spins_user_id', 'user_spins', ['user_id'], unique=False)
    op.create_index('idx_user_spins_created_at', 'user_spins', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_user_spins_created_at', table_name='user_spins')
    op.drop_index('idx_user_spins_user_id', table_name='user_spins')
    op.drop_table('user_spins')
    op.drop_table('spin_rewards')
    op.execute("DROP TYPE IF EXISTS spinrewardtype")
