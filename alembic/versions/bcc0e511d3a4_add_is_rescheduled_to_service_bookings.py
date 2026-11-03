"""add_is_rescheduled_to_service_bookings

Revision ID: bcc0e511d3a4
Revises: 49b5ea71ae3c
Create Date: 2026-11-03 10:20:27.770433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcc0e511d3a4'
down_revision: Union[str, Sequence[str], None] = '49b5ea71ae3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'service_bookings',
        sa.Column('is_rescheduled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('service_bookings', 'is_rescheduled')
