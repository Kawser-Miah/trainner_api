from datetime import datetime, timezone
from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.billing.user_billing_repository import (
    get_user_billing_orders,
)
from src.schemas.client.billing.user_billing_schemas import (
    UserBillingHistoryData,
    UserBillingHistoryItem,
)
from src.service.client.billing.helpers import build_billing_item_from_order


async def get_user_billing_history_service(
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> UserBillingHistoryData:
    """Retrieve billing history, metrics, and transactions for the authenticated client."""
    orders = get_user_billing_orders(db=db, user_id=current_user.id)

    total_spent_val = 0.0
    sessions_this_month = 0
    now = datetime.now(timezone.utc)
    current_month_prefix = f"{now.year:04d}-{now.month:02d}"

    items: list[UserBillingHistoryItem] = []

    for order in orders:
        if order.payment_status == "paid":
            try:
                total_spent_val += float(order.amount or "0.00")
            except (ValueError, TypeError):
                pass

            if order.order_type == "service" and order.booking_date:
                if str(order.booking_date).startswith(current_month_prefix):
                    sessions_this_month += 1

        items.append(build_billing_item_from_order(order=order, request=request))

    return UserBillingHistoryData(
        total_spent=f"{total_spent_val:.2f}",
        sessions_this_month=sessions_this_month,
        items=items,
    )

