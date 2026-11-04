"""add_paid_at_and_refunded_at_to_orders

Revision ID: 2ebcfef00ed9
Revises: bcc0e511d3a4
Create Date: 2026-11-04 14:44:10.930791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ebcfef00ed9'
down_revision: Union[str, Sequence[str], None] = 'bcc0e511d3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('orders', sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE orders SET paid_at = created_at WHERE payment_status IN ('paid', 'refunded') AND paid_at IS NULL")
    op.execute("UPDATE orders SET refunded_at = updated_at WHERE payment_status = 'refunded' AND refunded_at IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('orders', 'refunded_at')
    op.drop_column('orders', 'paid_at')
