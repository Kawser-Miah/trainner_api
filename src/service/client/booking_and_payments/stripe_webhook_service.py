import json
import stripe
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.client.service_order import ServiceOrder
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_service_order_by_id,
)


def verify_and_construct_webhook_event(payload_bytes: bytes, sig_header: str | None) -> dict:
    if settings.stripe_webhook_secret and settings.stripe_webhook_secret.strip():
        if not sig_header:
            raise AppException(
                message="Missing stripe-signature header.",
                status=400,
                error="MISSING_SIGNATURE",
            )
        try:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret.strip(),
            )
            return event.to_dict() if hasattr(event, "to_dict") else event
        except ValueError as e:
            raise AppException(
                message=f"Invalid webhook payload: {str(e)}",
                status=400,
                error="INVALID_PAYLOAD",
            )
        except stripe.error.SignatureVerificationError as e:
            raise AppException(
                message=f"Invalid webhook signature: {str(e)}",
                status=400,
                error="INVALID_SIGNATURE",
            )
    else:
        try:
            return json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            raise AppException(
                message="Invalid JSON payload.",
                status=400,
                error="INVALID_PAYLOAD",
            )


async def handle_stripe_webhook_service(
    payload_bytes: bytes,
    sig_header: str | None,
    db: Session,
) -> dict:
    event = verify_and_construct_webhook_event(payload_bytes, sig_header)
    if hasattr(event, "to_dict"):
        event = event.to_dict()

    event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", "")
    data_object = (
        event.get("data", {}).get("object", {})
        if isinstance(event, dict)
        else getattr(getattr(event, "data", None), "object", {})
    )
    if hasattr(data_object, "to_dict"):
        data_object = data_object.to_dict()

    if event_type in ["checkout.session.completed", "checkout.session.async_payment_succeeded"]:
        metadata = (
            data_object.get("metadata", {})
            if isinstance(data_object, dict)
            else getattr(data_object, "metadata", {})
        ) or {}
        if hasattr(metadata, "to_dict"):
            metadata = metadata.to_dict()

        booking_id = metadata.get("booking_id") if isinstance(metadata, dict) else getattr(metadata, "booking_id", None)
        if not booking_id:
            client_ref = (
                data_object.get("client_reference_id")
                if isinstance(data_object, dict)
                else getattr(data_object, "client_reference_id", None)
            )
            if client_ref and str(client_ref).isdigit():
                booking_id = client_ref

        session_id = (
            data_object.get("id")
            if isinstance(data_object, dict)
            else getattr(data_object, "id", None)
        )
        payment_intent = (
            data_object.get("payment_intent")
            if isinstance(data_object, dict)
            else getattr(data_object, "payment_intent", None)
        )

        trx_id = None
        if payment_intent:
            if isinstance(payment_intent, dict):
                trx_id = payment_intent.get("id")
            elif hasattr(payment_intent, "id"):
                trx_id = getattr(payment_intent, "id")
            else:
                trx_id = str(payment_intent)
        elif session_id:
            trx_id = str(session_id)

        order = None
        if booking_id:
            order = get_service_order_by_id(db=db, order_id=int(booking_id))
        elif session_id:
            order = (
                db.query(ServiceOrder)
                .filter(ServiceOrder.transaction_id == session_id)
                .first()
            )

        if order:
            order.payment_status = "paid"
            order.status = "confirmed"
            order.payment_method = "stripe"
            if trx_id:
                order.transaction_id = trx_id
            db.commit()
            return {
                "received": True,
                "event": event_type,
                "booking_id": order.id,
                "status": order.status,
                "payment_status": order.payment_status,
                "transaction_id": order.transaction_id,
            }

    elif event_type in ["checkout.session.async_payment_failed", "checkout.session.expired"]:
        metadata = (
            data_object.get("metadata", {})
            if isinstance(data_object, dict)
            else getattr(data_object, "metadata", {})
        ) or {}
        if hasattr(metadata, "to_dict"):
            metadata = metadata.to_dict()
        booking_id = metadata.get("booking_id") if isinstance(metadata, dict) else getattr(metadata, "booking_id", None)
        if booking_id:
            order = get_service_order_by_id(db=db, order_id=int(booking_id))
            if order and order.payment_status != "paid":
                order.payment_status = "failed" if "failed" in event_type else "expired"
                db.commit()
                return {
                    "received": True,
                    "event": event_type,
                    "booking_id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                }

    return {"received": True, "event": event_type}
