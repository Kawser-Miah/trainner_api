from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.client.browse.service_schemas import ProviderSummaryResponse


class DigitalProductCategoryDetails(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DigitalProductItemResponse(BaseModel):
    id: int
    coach: ProviderSummaryResponse | int | dict
    category: int
    category_details: DigitalProductCategoryDetails
    title: str
    description: str | None = None
    thumbnail: str | None = Field(default=None, serialization_alias="Thumbnail")
    book_file: str | None = None
    preview_file: str | None = None
    page_count: int | None = None
    preview_page_count: int | None = None
    file_type: str | None = "PDF"
    is_published: bool = True
    is_purchased: bool = False
    price: str = "0.00"
    status: str = "published"
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DigitalProductDetailResponse(DigitalProductItemResponse):
    other_products: list[DigitalProductItemResponse] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
