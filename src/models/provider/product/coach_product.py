from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class CoachProduct(Base):
    __tablename__ = "coach_products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    coach_profile_id: Mapped[int] = mapped_column(
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thumbnail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    book_file: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    preview_file: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    preview_page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    file_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    price: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="published",
        nullable=False,
    )

    sales_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    revenue: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    coach_profile = relationship(
        "CoachProfile",
        back_populates="products",
    )

    category = relationship(
        "Category",
    )

    @property
    def coach(self) -> int:
        return self.coach_profile_id
