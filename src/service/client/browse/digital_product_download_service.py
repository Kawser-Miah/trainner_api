from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import (
    get_browse_digital_product_detail,
    is_product_purchased_by_user,
)


async def download_digital_product_file_service(
    product_id: int,
    db: Session,
    current_user: User,
) -> tuple[bytes, str]:
    product = get_browse_digital_product_detail(db=db, product_id=product_id)
    if not product or not product.book_file:
        raise AppException(
            status=404,
            message="Digital product or file not found.",
            error="NOT_FOUND",
        )

    rel_path = product.book_file.lstrip("/\\")
    file_path = Path(rel_path)
    if not file_path.exists():
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
        return file_path.read_bytes(), "receipt.pdf"

    # For non-purchased users: serve preview file if generated, or extract 2-page preview
    if product.preview_file:
        preview_rel = product.preview_file.lstrip("/\\")
        preview_path = Path(preview_rel)
        if preview_path.exists():
            return preview_path.read_bytes(), "receipt.pdf"

    try:
        reader = PdfReader(str(file_path))
        writer = PdfWriter()
        total_pages = len(reader.pages)
        max_preview_pages = min(2, total_pages)
        for i in range(max_preview_pages):
            writer.add_page(reader.pages[i])

        buf = BytesIO()
        writer.write(buf)
        return buf.getvalue(), "receipt.pdf"
    except Exception:
        return file_path.read_bytes(), "receipt.pdf"
