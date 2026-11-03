"""Client My Booking routes package."""

from fastapi import APIRouter

from src.api.routes.client.mybooking.user_booking_detail import (
    router as user_booking_detail_router,
)
from src.api.routes.client.mybooking.user_booking_list import (
    router as user_booking_list_router,
)
from src.api.routes.client.mybooking.user_booking_reschedule import (
    router as user_booking_reschedule_router,
)

my_booking_router = APIRouter()
my_booking_router.include_router(user_booking_list_router)
my_booking_router.include_router(user_booking_detail_router)
my_booking_router.include_router(user_booking_reschedule_router)

__all__ = [
    "user_booking_list_router",
    "user_booking_detail_router",
    "user_booking_reschedule_router",
    "my_booking_router",
]

