"""Client Product services package alias."""

from src.service.client.myproduct import (
    get_user_purchased_products_service,
)

__all__ = ["get_user_purchased_products_service"]
