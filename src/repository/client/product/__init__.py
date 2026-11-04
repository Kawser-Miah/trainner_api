"""Client Product repository package alias."""

from src.repository.client.myproduct import (
    get_user_paid_product_order_by_id,
    get_user_paid_product_orders,
)

__all__ = [
    "get_user_paid_product_orders",
    "get_user_paid_product_order_by_id",
]
