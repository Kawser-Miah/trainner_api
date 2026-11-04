from pydantic import BaseModel, ConfigDict


class UserPurchasedProductItem(BaseModel):
    id: int
    coach_name: str = ""
    product_title: str = ""
    product_category: str = ""
    product_price: str = "0.00"
    payment_status: str = "paid"
    coach_profile_photo: str | None = None
    created_at: str
    Thumbnail: str | None = None
    book_file: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
