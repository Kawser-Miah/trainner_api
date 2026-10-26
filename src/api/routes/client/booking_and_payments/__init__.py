"""Client Booking & Payments routes package."""

from src.api.routes.client.booking_and_payments.book_service import router as book_service_router
from src.api.routes.client.booking_and_payments.stripe_checkout import router as stripe_checkout_router

__all__ = [
    "book_service_router",
    "stripe_checkout_router",
]
