from fastapi import APIRouter, Depends, Path, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.digital_product_download_service import (
    download_digital_product_file_service,
)

router = APIRouter(
    prefix=settings.digital_product_download_prefix,
    tags=["Client Browse Digital Products"],
)


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Digital Product Download",
    description="Download a digital product PDF file. Non-purchased clients receive a 2-page preview, while purchased clients or the coach receive the full document.",
)
@router.get(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def download_digital_product(
    product_id: int = Path(..., description="Digital Product ID"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    payload = await download_digital_product_file_service(
        product_id=product_id,
        db=db,
        current_user=current_user,
    )
    if payload.path is not None:
        return FileResponse(
            path=str(payload.path),
            filename=payload.filename,
            media_type=payload.media_type,
        )
    return Response(
        content=payload.content,
        media_type=payload.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{payload.filename}"',
        },
    )
