from src.api.routes.client.browse.coach_availability_date import (
    router as coach_availability_date_router,
)
from src.api.routes.client.browse.coach_availability_month import (
    router as coach_availability_month_router,
)

# Default router alias for backward compatibility
router = coach_availability_date_router

__all__ = [
    "router",
    "coach_availability_date_router",
    "coach_availability_month_router",
]
