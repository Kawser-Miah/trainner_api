from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.billing.user_billing_receipt_service import (
    generate_receipt_pdf,
    get_user_billing_receipt_service,
    render_receipt_html,
)

router = APIRouter(
    tags=["Client Billing"],
)


@router.get(
    f"{settings.user_billing_history_prefix}/{{order_id}}/receipt",
    status_code=status.HTTP_200_OK,
    summary="Get User Billing Receipt PDF",
    description="Retrieve binary PDF receipt for a paid or refunded booking.",
)
@router.get(
    f"{settings.user_billing_history_prefix}/{{order_id}}/receipt/",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_user_billing_receipt(
    order_id: int,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    receipt_data = await get_user_billing_receipt_service(
        db=db,
        current_user=current_user,
        order_id=order_id,
        request=request,
    )

    accept_header = request.headers.get("accept", "")
    format_query = request.query_params.get("format", "").lower()

    if format_query == "json" or (accept_header == "application/json" and format_query != "pdf"):
        return CommonResponse(
            success=True,
            code=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message="Receipt retrieved successfully.",
            data=receipt_data,
        )

    if format_query == "html" or "text/html" in accept_header:
        return HTMLResponse(content=render_receipt_html(receipt_data))

    pdf_bytes = generate_receipt_pdf(receipt_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="receipt.pdf"',
            "Content-Type": "application/pdf",
        },
    )
