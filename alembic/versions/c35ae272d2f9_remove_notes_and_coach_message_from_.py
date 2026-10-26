"""remove_notes_and_coach_message_from_service_orders

Revision ID: c35ae272d2f9
Revises: a7db21fb5384
Create Date: 2026-10-26 10:41:26.238810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c35ae272d2f9'
down_revision: Union[str, Sequence[str], None] = 'a7db21fb5384'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('service_orders', 'notes')
    op.drop_column('service_orders', 'coach_message')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('service_orders', sa.Column('coach_message', sa.Text(), nullable=False, server_default=''))
    op.add_column('service_orders', sa.Column('notes', sa.Text(), nullable=True))
