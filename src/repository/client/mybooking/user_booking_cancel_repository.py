from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.client.order import Order


def mark_order_cancelled_and_refunded(db: Session, order: Order) -> Order:
    """Update order status to cancelled and payment_status to refunded in database."""
    order.status = "cancelled"
    order.payment_status = "refunded"
    order.refunded_at = datetime.now(timezone.utc)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
