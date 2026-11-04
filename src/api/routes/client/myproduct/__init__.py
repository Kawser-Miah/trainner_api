"""Client My Product routes package."""

from fastapi import APIRouter

from src.api.routes.client.myproduct.user_product_detail import (
    router as user_product_detail_router,
)
from src.api.routes.client.myproduct.user_product_list import (
    router as user_product_list_router,
)

my_product_router = APIRouter()
my_product_router.include_router(user_product_list_router)
my_product_router.include_router(user_product_detail_router)

__all__ = [
    "user_product_list_router",
    "user_product_detail_router",
    "my_product_router",
]
