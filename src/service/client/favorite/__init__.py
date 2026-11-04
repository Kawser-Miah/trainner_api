"""Client Favorites services package."""

from src.service.client.favorite.favorite_service import (
    add_coach_favorite_service,
    get_user_favorites_service,
    remove_coach_favorite_service,
)

__all__ = [
    "add_coach_favorite_service",
    "get_user_favorites_service",
    "remove_coach_favorite_service",
]
