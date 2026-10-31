import mimetypes
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.utils.uploads import resolve_media_path
from src.repository.client.browse.client_browse_repository import (
    get_browse_digital_product_detail,
    is_product_purchased_by_user,
)


@dataclass(frozen=True)
class DownloadPayload:
    filename: str
    media_type: str
    path: Path | None = None
    content: bytes | None = None


def _download_filename(title: str | None, file_path: Path) -> str:
    # PDFs keep the filename existing clients already expect.
    if file_path.suffix.lower() == ".pdf":
        return "receipt.pdf"
    stem = re.sub(r"[^\w\-]+", "_", title or "").strip("_") or file_path.stem
    return f"{stem}{file_path.suffix}"


async def download_digital_product_file_service(
    product_id: int,
    db: Session,
    current_user: User,
) -> DownloadPayload:
    product = get_browse_digital_product_detail(db=db, product_id=product_id)
    if not product or not product.book_file:
        raise AppException(
            status=404,
            message="Digital product or file not found.",
            error="NOT_FOUND",
        )

    file_path = resolve_media_path(product.book_file)
    if file_path is None or not file_path.is_file():
        raise AppException(
            status=404,
            message="Digital product file not found on server.",
            error="FILE_NOT_FOUND",
        )

    is_purchased = is_product_purchased_by_user(
        db=db,
        user_id=current_user.id,
        product=product,
    )

    if is_purchased:
        media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        return DownloadPayload(
            filename=_download_filename(product.title, file_path),
            media_type=media_type,
            path=file_path,
        )

    # Non-purchased users only ever get a PDF preview: the generated one, or the first 2 pages.
    preview_name = "receipt.pdf"
    preview_path = resolve_media_path(product.preview_file) if product.preview_file else None
    if preview_path is not None and preview_path.is_file():
        return DownloadPayload(filename=preview_name, media_type="application/pdf", path=preview_path)

    if file_path.suffix.lower() != ".pdf":
        raise AppException(
            status=403,
            message="Purchase this product to download it.",
            error="PURCHASE_REQUIRED",
        )

    try:
        reader = PdfReader(str(file_path))
        writer = PdfWriter()
        for i in range(min(2, len(reader.pages))):
            writer.add_page(reader.pages[i])

        buf = BytesIO()
        writer.write(buf)
        return DownloadPayload(filename=preview_name, media_type="application/pdf", content=buf.getvalue())
    except Exception:
        # Never fall back to the full file for someone who has not purchased it.
        raise AppException(
            status=403,
            message="Purchase this product to download it.",
            error="PURCHASE_REQUIRED",
        )
