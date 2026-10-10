from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.core.common_responses import CommonResponse


class CoachUserSummaryResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str = ""
    address: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CoachCategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool = True
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CoachCertificationResponse(BaseModel):
    id: int
    name: str
    document: str | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CoachQualificationResponse(BaseModel):
    id: int
    name: str
    document: str | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CoachProfileDataResponse(BaseModel):
    id: int
    user: CoachUserSummaryResponse
    profile_photo: str | None = None
    headline: str | None = None
    about: str | None = None
    categories: list[CoachCategoryResponse] = Field(default_factory=list)
    certifications: list[CoachCertificationResponse] = Field(default_factory=list)
    qualifications: list[CoachQualificationResponse] = Field(default_factory=list)
    introduction_video: str | None = None
    introduction_video_duration: int | None = 0
    introduction_video_duration_display: str = "0:00"
    introduction_video_thumbnail: str | None = None
    linkedin_url: str | None = None
    affiliate_commission_percent: str = "20.00"
    auto_approve_affiliates: bool = False
    expertises: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    is_completed: bool = True
    status: str = "pending"
    rejection_reason: str = ""
    avg_rating: float = 0.0
    total_reviews: int = 0
    completed_sessions_count: int = 0
    success_rate: float | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


CoachProfileResponse = CommonResponse
