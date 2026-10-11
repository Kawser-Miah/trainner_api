from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ServiceBenefitCreateRequest(BaseModel):
    outcome: str


class ServiceBenefitResponse(BaseModel):
    id: int
    outcome: str

    model_config = ConfigDict(from_attributes=True)


class ServiceCategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CreateCoachServiceRequest(BaseModel):
    title: str
    category: int = Field(..., description="Category ID")
    description: str | None = None
    service_type: str = "one_time"
    session_format: str = "video"
    session_duration: int = 60
    currency: str = "USD"
    price: str = "0.00"
    booking_type: str = "instant"
    who_is_this_service_for: str | None = None
    preparation_instructions: str | None = None
    cancellation_policy: str = "standard"
    session_url: str | None = None
    status: str = "published"
    benefits: list[ServiceBenefitCreateRequest] = Field(default_factory=list)

    @field_validator("price", mode="before")
    @classmethod
    def format_price(cls, v: Any) -> str:
        if v is None:
            return "0.00"
        try:
            val_float = float(v)
            return f"{val_float:.2f}"
        except (ValueError, TypeError):
            return str(v)


class UpdateCoachServiceRequest(BaseModel):
    title: str | None = None
    category: int | None = None
    description: str | None = None
    service_type: str | None = None
    session_format: str | None = None
    session_duration: int | None = None
    currency: str | None = None
    price: str | None = None
    booking_type: str | None = None
    who_is_this_service_for: str | None = None
    preparation_instructions: str | None = None
    cancellation_policy: str | None = None
    session_url: str | None = None
    status: str | None = None
    benefits: list[ServiceBenefitCreateRequest] | None = None

    @field_validator("price", mode="before")
    @classmethod
    def format_price(cls, v: Any) -> str | None:
        if v is None:
            return None
        try:
            val_float = float(v)
            return f"{val_float:.2f}"
        except (ValueError, TypeError):
            return str(v)


class CoachServiceDataResponse(BaseModel):
    id: int
    coach: int
    title: str
    description: str | None = None
    service_type: str
    session_format: str
    session_duration: int
    currency: str
    price: str
    booking_type: str
    who_is_this_service_for: str | None = None
    preparation_instructions: str | None = None
    cancellation_policy: str
    session_url: str | None = None
    status: str
    benefits: list[ServiceBenefitResponse] = Field(default_factory=list)
    category: ServiceCategoryResponse | None = None
    bookings_count: int = 0
    revenue: str = "0.00"
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class DeleteCoachServiceDataResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
