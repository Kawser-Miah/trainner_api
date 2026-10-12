from typing import Any
from pydantic import BaseModel, ConfigDict


class ClientCoachUserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str = ""
    address: str | None = None
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClientCoachCertificationResponse(BaseModel):
    id: int
    name: str
    document: str | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ClientCoachQualificationResponse(BaseModel):
    id: int
    name: str
    document: str | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CoachProfileListItemResponse(BaseModel):
    id: int
    user: ClientCoachUserResponse
    categories: list[str] = []
    avg_rating: float = 0.0
    review_count: int = 0
    completed_sessions_count: int = 0
    starting_price: str | None = None
    is_favorited: bool = False
    profile_photo: str | None = None
    introduction_video: str | None = None
    introduction_video_duration: int | None = None
    introduction_video_thumbnail: str | None = None
    linkedin_url: str | None = None
    affiliate_commission_percent: str = "20.00"
    on_call_enabled: bool = False
    auto_approve_affiliates: bool = True
    about: str | None = None
    headline: str | None = None
    expertises: list[str] = []
    languages: list[str] = []
    is_completed: bool = True
    status: str = "approved"
    rejection_reason: str = ""
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class MissedMeetingsResponse(BaseModel):
    missed: int = 0
    total: int = 0
    ratio: str = "0/0"
    percent: float = 0.0


class CoachProfileDetailResponse(BaseModel):
    id: int
    user: ClientCoachUserResponse
    profile_photo: str | None = None
    introduction_video: str | None = None
    introduction_video_duration: int | None = None
    introduction_video_duration_display: str | None = None
    introduction_video_thumbnail: str | None = None
    linkedin_url: str | None = None
    affiliate_status: str | None = None
    affiliate_code: str | None = None
    affiliate_commission_percent: str = "20.00"
    headline: str | None = None
    about: str | None = None
    expertises: list[str] = []
    languages: list[str] = []
    is_completed: bool = True
    status: str = "approved"
    categories: list[str] = []
    certifications: list[ClientCoachCertificationResponse] = []
    qualifications: list[ClientCoachQualificationResponse] = []
    services: list[dict[str, Any]] = []
    products: list[dict[str, Any]] = []
    blogs: list[dict[str, Any]] = []
    avg_rating: float = 0.0
    review_count: int = 0
    completed_sessions_count: int = 0
    success_rate: float | int | None = None
    missed_meetings: MissedMeetingsResponse = MissedMeetingsResponse()
    takes_on_call: bool = False
    starting_price: str | None = None
    is_favorited: bool = False
    reviews: list[dict[str, Any]] = []
    rating_breakdown: dict[str, int] = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
