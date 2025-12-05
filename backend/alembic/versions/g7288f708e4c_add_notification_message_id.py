"""add notification_message_id to requests

Revision ID: g7288f708e4c
Revises: f6277f607d3b
Create Date: 2025-12-05 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g7288f708e4c'
down_revision: Union[str, Sequence[str], None] = 'f6277f607d3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification_message_id to deposit_requests
    op.add_column(
        'deposit_requests',
        sa.Column('notification_message_id', sa.Integer(), nullable=True)
    )

    # Add notification_message_id to withdraw_requests
    op.add_column(
        'withdraw_requests',
        sa.Column('notification_message_id', sa.Integer(), nullable=True)
    )

    # Fix foreign keys for confirmed_by and processed_by to point to admins table
    # First drop old constraints if they exist
    try:
        op.drop_constraint('deposit_requests_confirmed_by_fkey', 'deposit_requests', type_='foreignkey')
    except Exception:
        pass

    try:
        op.drop_constraint('withdraw_requests_processed_by_fkey', 'withdraw_requests', type_='foreignkey')
    except Exception:
        pass

    # Add new foreign key constraints pointing to admins
    op.create_foreign_key(
        'deposit_requests_confirmed_by_fkey',
        'deposit_requests',
        'admins',
        ['confirmed_by'],
        ['id']
    )

    op.create_foreign_key(
        'withdraw_requests_processed_by_fkey',
        'withdraw_requests',
        'admins',
        ['processed_by'],
        ['id']
    )


def downgrade() -> None:
    # Remove foreign key constraints
    op.drop_constraint('deposit_requests_confirmed_by_fkey', 'deposit_requests', type_='foreignkey')
    op.drop_constraint('withdraw_requests_processed_by_fkey', 'withdraw_requests', type_='foreignkey')

    # Restore old foreign keys pointing to users
    op.create_foreign_key(
        'deposit_requests_confirmed_by_fkey',
        'deposit_requests',
        'users',
        ['confirmed_by'],
        ['id']
    )

    op.create_foreign_key(
        'withdraw_requests_processed_by_fkey',
        'withdraw_requests',
        'users',
        ['processed_by'],
        ['id']
    )

    # Remove notification_message_id columns
    op.drop_column('withdraw_requests', 'notification_message_id')
    op.drop_column('deposit_requests', 'notification_message_id')
