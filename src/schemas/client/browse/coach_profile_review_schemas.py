from pydantic import BaseModel, ConfigDict, Field


class CoachProfileReviewCreateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review: str = Field(..., min_length=1, description="Review text")

    model_config = ConfigDict(extra="ignore")


class CoachProfileReviewData(BaseModel):
    id: int
    coach: int
    coach_name: str
    user: int
    user_name: str
    rating: int
    review: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
