"""Client Booking & Payments routes package."""

from src.api.routes.client.booking_and_payments.book_service import router as book_service_router
from src.api.routes.client.booking_and_payments.product_purchase import router as product_purchase_router
from src.api.routes.client.booking_and_payments.user_booking_list import router as user_booking_list_router
from src.api.routes.client.booking_and_payments.stripe_checkout import router as stripe_checkout_router

__all__ = [
    "book_service_router",
    "product_purchase_router",
    "stripe_checkout_router",
    "user_booking_list_router",
]
