from io import BytesIO
from fastapi import Request
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.billing.user_billing_repository import (
    get_user_billing_order_by_id,
)
from src.schemas.client.billing.user_billing_schemas import (
    UserBillingReceiptData,
)
from src.service.client.billing.helpers import _format_iso


async def get_user_billing_receipt_service(
    db: Session,
    current_user: User,
    order_id: int,
    request: Request | None = None,
) -> UserBillingReceiptData:
    """Retrieve detailed billing receipt data for the authenticated client."""
    order = get_user_billing_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )
    if not order:
        raise AppException(
            message="Receipt not found.",
            status=404,
            error="RECEIPT_NOT_FOUND",
        )

    coach_user = order.coach or (
        order.coach_profile.user if order.coach_profile else None
    )
    coach_name = coach_user.full_name if coach_user and coach_user.full_name else "Coach"

    if order.order_type == "product":
        title = order.product.title if order.product else "Digital Product"
    else:
        title = order.service.title if order.service else "Coaching Session"

    paid_at_dt = order.paid_at or (
        order.created_at if order.payment_status in ("paid", "refunded") else None
    )
    paid_at_str = _format_iso(paid_at_dt)

    refunded_at_dt = None
    if order.payment_status == "refunded":
        refunded_at_dt = order.refunded_at or order.updated_at
    refunded_at_str = _format_iso(refunded_at_dt)

    receipt_number = f"REC-{order.id:06d}"

    return UserBillingReceiptData(
        order_id=order.id,
        receipt_number=receipt_number,
        type=order.order_type,
        title=title,
        coach_name=coach_name,
        client_name=current_user.full_name or "Client",
        amount=order.amount or "0.00",
        client_fee=order.client_fee or "0.00",
        total_amount=order.total_amount or order.amount or "0.00",
        currency=order.currency or "USD",
        status=order.payment_status,
        booking_status=order.status,
        booking_date=order.booking_date,
        booking_time=order.booking_time,
        transaction_id=order.transaction_id,
        paid_at=paid_at_str,
        refunded_at=refunded_at_str,
    )


def _pdf_escape(text: str | None) -> str:
    """Escape string for PDF literal text format."""
    if not text:
        return ""
    safe = str(text).replace("\\", "\\\\").replace("(", "\\[").replace(")", "\\]")
    return safe.encode("latin1", "replace").decode("latin1")


def _format_display_dt(dt_str: str | None) -> str:
    """Format raw ISO or date string into clean human-readable date and time (e.g. Nov 04, 2026, 12:53 PM)."""
    if not dt_str:
        return "N/A"
    try:
        from datetime import datetime
        clean = str(dt_str).replace("Z", "+00:00")
        if "T" in clean or " " in clean:
            dt = datetime.fromisoformat(clean)
            return dt.strftime("%b %d, %Y, %I:%M %p")
        if len(clean) == 10 and clean.count("-") == 2:
            dt = datetime.strptime(clean, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")
        return str(dt_str)
    except Exception:
        return str(dt_str)


def generate_receipt_pdf(data: UserBillingReceiptData) -> bytes:
    """Generate a clean binary PDF receipt for the given billing order."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    cmds: list[str] = []

    # Brand Title
    cmds.append("0.06 0.09 0.16 rg")
    cmds.append(f"BT /F2 22 Tf 50 725 Td ({_pdf_escape('COACH HUB')}) Tj ET")

    # Document Subtitle & Receipt Number
    cmds.append("0.40 0.45 0.55 rg")
    cmds.append(f"BT /F1 12 Tf 50 705 Td ({_pdf_escape('OFFICIAL RECEIPT / INVOICE')}) Tj ET")
    cmds.append(f"BT /F2 12 Tf 460 725 Td ({_pdf_escape(data.receipt_number)}) Tj ET")

    # Status Badge Box
    is_paid = data.status.lower() == "paid"
    status_label = "PAID" if is_paid else "REFUNDED"
    if is_paid:
        cmds.append("0.06 0.70 0.40 rg 482 695 80 22 re f")
        cmds.append("1.0 1.0 1.0 rg")
        cmds.append(f"BT /F2 10 Tf 508 702 Td ({status_label}) Tj ET")
    else:
        cmds.append("0.90 0.25 0.25 rg 462 695 100 22 re f")
        cmds.append("1.0 1.0 1.0 rg")
        cmds.append(f"BT /F2 10 Tf 482 702 Td ({status_label}) Tj ET")

    # Separator Line
    cmds.append("0.85 0.88 0.92 RG 1 w 50 675 m 562 675 l S")

    # Metadata Details
    y = 640
    rows = [
        ("Item / Service:", data.title),
        ("Order Type:", data.type.capitalize()),
        ("Coach Name:", data.coach_name),
        ("Customer Name:", data.client_name),
        ("Booking Status:", data.booking_status.capitalize()),
        ("Payment Status:", data.status.capitalize()),
        ("Transaction ID:", data.transaction_id or "N/A"),
    ]
    if data.type.lower() == "service" and data.booking_date:
        session_time_str = f" at {data.booking_time}" if data.booking_time else ""
        rows.append(("Scheduled Session:", f"{_format_display_dt(data.booking_date)}{session_time_str}"))

    rows.append(("Payment Date:", _format_display_dt(data.paid_at)))
    if data.refunded_at:
        rows.append(("Refunded Date:", _format_display_dt(data.refunded_at)))

    for label, val in rows:
        cmds.append("0.40 0.45 0.55 rg")
        cmds.append(f"BT /F1 11 Tf 50 {y} Td ({_pdf_escape(label)}) Tj ET")
        cmds.append("0.09 0.13 0.20 rg")
        cmds.append(f"BT /F2 11 Tf 220 {y} Td ({_pdf_escape(val)}) Tj ET")
        cmds.append(f"0.94 0.95 0.96 RG 0.5 w 50 {y - 6} m 562 {y - 6} l S")
        y -= 26

    # Financial Breakdown
    y -= 14
    cmds.append("0.40 0.45 0.55 rg")
    cmds.append(f"BT /F1 11 Tf 50 {y} Td ({_pdf_escape('Subtotal:')}) Tj ET")
    cmds.append("0.09 0.13 0.20 rg")
    cmds.append(f"BT /F2 11 Tf 440 {y} Td ({_pdf_escape(data.amount + ' ' + data.currency)}) Tj ET")
    y -= 24

    cmds.append("0.40 0.45 0.55 rg")
    cmds.append(f"BT /F1 11 Tf 50 {y} Td ({_pdf_escape('Client Fee:')}) Tj ET")
    cmds.append("0.09 0.13 0.20 rg")
    cmds.append(f"BT /F2 11 Tf 440 {y} Td ({_pdf_escape(data.client_fee + ' ' + data.currency)}) Tj ET")
    y -= 22

    # Total Amount Highlight Box (drawn below Client Fee with proper margins)
    box_height = 42
    box_y = y - box_height
    cmds.append(f"0.94 0.96 0.99 rg 50 {box_y} 512 {box_height} re f")
    cmds.append("0.06 0.09 0.16 rg")
    cmds.append(f"BT /F2 13 Tf 70 {box_y + 15} Td ({_pdf_escape('Total Paid:')}) Tj ET")
    cmds.append(f"BT /F2 13 Tf 440 {box_y + 15} Td ({_pdf_escape(data.total_amount + ' ' + data.currency)}) Tj ET")

    # Footer Note
    footer_y = box_y - 40
    cmds.append("0.55 0.60 0.68 rg")
    cmds.append(
        f"BT /F1 10 Tf 50 {footer_y} Td ({_pdf_escape('Thank you for choosing Coach Hub. Please keep this receipt for your records.')}) Tj ET"
    )

    stream_content = " ".join(cmds).encode("latin1")
    stream_obj = DecodedStreamObject()
    stream_obj.set_data(stream_content)
    stream_ref = writer._add_object(stream_obj)
    page[NameObject("/Contents")] = stream_ref

    font_regular = writer._add_object(
        DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
    )
    font_bold = writer._add_object(
        DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica-Bold"),
        })
    )

    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): font_regular,
            NameObject("/F2"): font_bold,
        })
    })

    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def render_receipt_html(data: UserBillingReceiptData) -> str:
    """Render a clean, printable HTML invoice/receipt for browser rendering."""
    status_color = "#10b981" if data.status == "paid" else "#ef4444"
    refund_section = (
        f"<div style='margin-top: 8px; color: #ef4444; font-size: 13px;'>Refunded at: {data.refunded_at}</div>"
        if data.refunded_at
        else ""
    )

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Receipt {data.receipt_number}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px 20px; }}
        .receipt-card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); padding: 32px; border: 1px solid #e2e8f0; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 24px; }}
        .brand {{ font-size: 24px; font-weight: 700; color: #0f172a; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; color: #fff; background: {status_color}; }}
        .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }}
        .label {{ color: #64748b; font-size: 14px; }}
        .val {{ font-weight: 600; font-size: 14px; text-align: right; }}
        .total-row {{ display: flex; justify-content: space-between; padding: 16px 0 0 0; margin-top: 12px; font-size: 18px; font-weight: 700; color: #0f172a; }}
        .footer {{ margin-top: 32px; text-align: center; color: #94a3b8; font-size: 12px; }}
        @media print {{ body {{ background: #fff; padding: 0; }} .receipt-card {{ box-shadow: none; border: none; }} }}
    </style>
</head>
<body>
    <div class="receipt-card">
        <div class="header">
            <div>
                <div class="brand">Coach Hub</div>
                <div style="color: #64748b; font-size: 13px; margin-top: 4px;">{data.receipt_number}</div>
            </div>
            <div>
                <span class="badge">{data.status}</span>
                {refund_section}
            </div>
        </div>
        <div class="row"><span class="label">Item</span><span class="val">{data.title}</span></div>
        <div class="row"><span class="label">Type</span><span class="val">{data.type.capitalize()}</span></div>
        <div class="row"><span class="label">Coach</span><span class="val">{data.coach_name}</span></div>
        <div class="row"><span class="label">Customer</span><span class="val">{data.client_name}</span></div>
        <div class="row"><span class="label">Payment Date</span><span class="val">{_format_display_dt(data.paid_at)}</span></div>
        <div class="row"><span class="label">Transaction ID</span><span class="val">{data.transaction_id or "-"}</span></div>
        <div class="row"><span class="label">Subtotal</span><span class="val">{data.amount} {data.currency}</span></div>
        <div class="row"><span class="label">Client Fee</span><span class="val">{data.client_fee} {data.currency}</span></div>
        <div class="total-row"><span>Total Paid</span><span>{data.total_amount} {data.currency}</span></div>
        <div class="footer">Thank you for your purchase. Keep this receipt for your records.</div>
    </div>
</body>
</html>
"""
