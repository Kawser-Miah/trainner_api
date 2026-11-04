"""Client Product routes package alias."""

from src.api.routes.client.myproduct import (
    my_product_router,
    user_product_list_router,
)

__all__ = [
    "user_product_list_router",
    "my_product_router",
]
