from pydantic import BaseModel, ConfigDict


class ClientCoachReviewItem(BaseModel):
    id: int
    user_name: str
    user_image: str | None = None
    rating: int
    review: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ClientCoachReviewsResponse(BaseModel):
    coach_profile_id: int
    avg_rating: float = 0.0
    review_count: int = 0
    rating_breakdown: dict[str, int] = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    reviews: list[ClientCoachReviewItem] = []

    model_config = ConfigDict(from_attributes=True)
