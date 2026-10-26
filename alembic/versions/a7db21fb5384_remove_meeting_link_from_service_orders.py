"""remove_meeting_link_from_service_orders

Revision ID: a7db21fb5384
Revises: aefc43ae7ef6
Create Date: 2026-10-26 10:24:58.919204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7db21fb5384'
down_revision: Union[str, Sequence[str], None] = 'aefc43ae7ef6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('service_orders', 'meeting_link')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('service_orders', sa.Column('meeting_link', sa.String(length=500), nullable=True))
