from typing import Any
from pydantic import BaseModel, ConfigDict


class ClientServiceProviderDetails(BaseModel):
    id: int
    coach_profile_id: int
    full_name: str
    email: str
    phone_number: str = ""
    address: str | None = None
    rating: float = 0.0
    review_count: int = 0
    headline: str | None = None
    profile_photo: str | None = None
    about: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClientServiceCategory(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClientServiceItemResponse(BaseModel):
    id: int
    coach_id: int
    coach_profile_id: int
    provider_details: ClientServiceProviderDetails
    title: str
    description: str | None = None
    service_type: str = "one_time"
    service_type_display: str = "One Time Session"
    session_format: str = "video"
    session_format_display: str = "Video Call"
    session_duration: int = 60
    currency: str = "USD"
    price: str = "0.00"
    booking_type: str = "instant"
    booking_type_display: str = "Instant Booking"
    who_is_this_service_for: str | None = None
    preparation_instructions: str | None = None
    cancellation_policy: str = "standard"
    cancellation_policy_display: str = "Standard"
    session_url: str | None = None
    status: str = "published"
    category: ClientServiceCategory | None = None
    benefits: list[str] = []
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ClientServiceDetailResponse(ClientServiceItemResponse):
    other_sessions: list[ClientServiceItemResponse] = []
