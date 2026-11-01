"""separate_orders_and_service_bookings

Revision ID: 49b5ea71ae3c
Revises: c35ae272d2f9
Create Date: 2026-11-01 10:46:23.071080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49b5ea71ae3c'
down_revision: Union[str, Sequence[str], None] = 'c35ae272d2f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Separate orders, service_bookings, and link product_purchases."""
    # 1. Rename table service_orders -> orders
    op.rename_table('service_orders', 'orders')

    # Rename primary key constraint and indexes
    op.execute("ALTER INDEX IF EXISTS service_orders_pkey RENAME TO orders_pkey")
    op.execute("ALTER INDEX IF EXISTS ix_service_orders_coach_id RENAME TO ix_orders_coach_id")
    op.execute("ALTER INDEX IF EXISTS ix_service_orders_coach_profile_id RENAME TO ix_orders_coach_profile_id")
    op.execute("ALTER INDEX IF EXISTS ix_service_orders_user_id RENAME TO ix_orders_user_id")
    op.execute("ALTER INDEX IF EXISTS ix_service_orders_service_id RENAME TO ix_orders_service_id")
    op.execute("ALTER INDEX IF EXISTS ix_service_orders_product_id RENAME TO ix_orders_product_id")

    # 2. Create service_bookings table
    op.create_table(
        'service_bookings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('booking_date', sa.String(length=50), nullable=True),
        sa.Column('booking_time', sa.String(length=50), nullable=True),
        sa.Column('is_on_call', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('payment_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['coach_services.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index(op.f('ix_service_bookings_order_id'), 'service_bookings', ['order_id'], unique=True)
    op.create_index(op.f('ix_service_bookings_service_id'), 'service_bookings', ['service_id'], unique=False)

    # 3. Migrate existing service bookings
    op.execute("""
        INSERT INTO service_bookings (order_id, service_id, booking_date, booking_time, is_on_call, payment_due_at, created_at, updated_at)
        SELECT id, service_id, booking_date, booking_time, is_on_call, payment_due_at, created_at, updated_at
        FROM orders
        WHERE order_type = 'service'
    """)

    # 4. Add order_id to product_purchases
    op.add_column('product_purchases', sa.Column('order_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('uq_product_purchases_order_id', 'product_purchases', ['order_id'])
    op.create_foreign_key('fk_product_purchases_order_id', 'product_purchases', 'orders', ['order_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_product_purchases_order_id'), 'product_purchases', ['order_id'], unique=True)

    # 5. Link existing product purchases
    op.execute("""
        UPDATE product_purchases p
        SET order_id = o.id
        FROM orders o
        WHERE o.order_type = 'product' AND o.user_id = p.user_id AND o.product_id = p.product_id
        AND p.order_id IS NULL
    """)

    # 6. Drop legacy columns from orders
    op.drop_constraint('service_orders_service_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('service_orders_product_id_fkey', 'orders', type_='foreignkey')
    op.drop_index('ix_orders_service_id', table_name='orders')
    op.drop_index('ix_orders_product_id', table_name='orders')
    op.drop_column('orders', 'service_id')
    op.drop_column('orders', 'product_id')
    op.drop_column('orders', 'booking_date')
    op.drop_column('orders', 'booking_time')
    op.drop_column('orders', 'is_on_call')
    op.drop_column('orders', 'payment_due_at')


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add columns to orders
    op.add_column('orders', sa.Column('payment_due_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('is_on_call', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('orders', sa.Column('booking_time', sa.String(length=50), nullable=True))
    op.add_column('orders', sa.Column('booking_date', sa.String(length=50), nullable=True))
    op.add_column('orders', sa.Column('product_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('service_id', sa.Integer(), nullable=True))
    op.create_index('ix_orders_product_id', 'orders', ['product_id'], unique=False)
    op.create_index('ix_orders_service_id', 'orders', ['service_id'], unique=False)
    op.create_foreign_key('service_orders_product_id_fkey', 'orders', 'coach_products', ['product_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('service_orders_service_id_fkey', 'orders', 'coach_services', ['service_id'], ['id'], ondelete='SET NULL')

    # Restore data back into orders
    op.execute("""
        UPDATE orders o
        SET service_id = sb.service_id,
            booking_date = sb.booking_date,
            booking_time = sb.booking_time,
            is_on_call = sb.is_on_call,
            payment_due_at = sb.payment_due_at
        FROM service_bookings sb
        WHERE o.id = sb.order_id
    """)

    op.execute("""
        UPDATE orders o
        SET product_id = pp.product_id
        FROM product_purchases pp
        WHERE o.id = pp.order_id
    """)

    # Drop product_purchases order_id
    op.drop_constraint('fk_product_purchases_order_id', 'product_purchases', type_='foreignkey')
    op.drop_constraint('uq_product_purchases_order_id', 'product_purchases', type_='unique')
    op.drop_index(op.f('ix_product_purchases_order_id'), table_name='product_purchases')
    op.drop_column('product_purchases', 'order_id')

    # Drop service_bookings
    op.drop_index(op.f('ix_service_bookings_service_id'), table_name='service_bookings')
    op.drop_index(op.f('ix_service_bookings_order_id'), table_name='service_bookings')
    op.drop_table('service_bookings')

    # Rename indexes back
    op.execute("ALTER INDEX IF EXISTS ix_orders_product_id RENAME TO ix_service_orders_product_id")
    op.execute("ALTER INDEX IF EXISTS ix_orders_service_id RENAME TO ix_service_orders_service_id")
    op.execute("ALTER INDEX IF EXISTS ix_orders_user_id RENAME TO ix_service_orders_user_id")
    op.execute("ALTER INDEX IF EXISTS ix_orders_coach_profile_id RENAME TO ix_service_orders_coach_profile_id")
    op.execute("ALTER INDEX IF EXISTS ix_orders_coach_id RENAME TO ix_service_orders_coach_id")
    op.execute("ALTER INDEX IF EXISTS orders_pkey RENAME TO service_orders_pkey")

    # Rename orders -> service_orders
    op.rename_table('orders', 'service_orders')
