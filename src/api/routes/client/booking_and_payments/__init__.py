"""Client Booking & Payments routes package."""

from src.api.routes.client.booking_and_payments.book_service import router as book_service_router

__all__ = [
    "book_service_router",
]
