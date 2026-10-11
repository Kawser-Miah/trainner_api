from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CoachProductCategoryDetailsResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CreateCoachProductRequest(BaseModel):
    title: str
    category: int = Field(..., description="Category ID")
    description: str | None = None
    price: str = "0.00"
    status: str = "published"

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


class UpdateCoachProductRequest(BaseModel):
    title: str | None = None
    category: int | None = None
    description: str | None = None
    price: str | None = None
    status: str | None = None

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


class CoachProductDataResponse(BaseModel):
    id: int
    coach: int
    category: int
    category_details: CoachProductCategoryDetailsResponse | None = None
    title: str
    description: str | None = None
    Thumbnail: str | None = Field(default=None, serialization_alias="Thumbnail")
    download_url: str | None = None
    preview_file: str | None = None
    page_count: int | None = None
    preview_page_count: int | None = None
    file_type: str | None = None
    price: str
    status: str
    sales_count: int = 0
    revenue: str = "0.00"
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DeleteCoachProductDataResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
