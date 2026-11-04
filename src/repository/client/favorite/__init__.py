"""Client Favorites repository package."""

from src.repository.client.favorite.favorite_repository import (
    add_favorite,
    get_coach_profile_by_id,
    get_favorite,
    get_user_favorite_coaches,
    is_coach_favorited,
    remove_favorite,
)

__all__ = [
    "add_favorite",
    "get_coach_profile_by_id",
    "get_favorite",
    "get_user_favorite_coaches",
    "is_coach_favorited",
    "remove_favorite",
]
