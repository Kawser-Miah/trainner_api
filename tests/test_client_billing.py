from datetime import datetime, timezone
import pytest
from sqlalchemy import select
from starlette.testclient import TestClient

from src.core.database import SessionLocal
from src.main import app
from src.models.accounts.user import User
from src.models.client.order import Order
from src.models.client.product_purchase import ProductPurchase
from src.models.client.service_booking import ServiceBooking
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.product.coach_product import CoachProduct
from src.models.provider.service.coach_service import CoachService
from src.utils.jwt import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def setup_billing_data(db_session):
    # 1. Coach
    coach = db_session.execute(
        select(User).where(User.email == "billing_coach@test.com")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Sarah Chen",
            email="billing_coach@test.com",
            password_hash="pw_hash",
            phone="+1234567890",
            photo_url="coach/profile/sarah.gif",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(coach)
        db_session.commit()
        db_session.refresh(coach)

    profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == coach.id)
    ).scalar_one_or_none()
    if not profile:
        profile = CoachProfile(
            user_id=coach.id,
            headline="Sarah Chen - Business Coach",
            about="Executive Coaching",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    category = db_session.execute(
        select(Category).where(Category.name == "Billing Category")
    ).scalar_one_or_none()
    if not category:
        category = Category(
            name="Billing Category",
            description="Category for billing tests",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

    # 2. Service
    service = db_session.execute(
        select(CoachService).where(CoachService.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not service:
        service = CoachService(
            coach_profile_id=profile.id,
            category_id=category.id,
            title="Strategy Session",
            description="1-on-1 strategy coaching",
            price="150.00",
            currency="USD",
            session_duration=60,
            status="published",
        )
        db_session.add(service)
        db_session.commit()
        db_session.refresh(service)

    # 3. Product
    product = db_session.execute(
        select(CoachProduct).where(CoachProduct.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not product:
        product = CoachProduct(
            coach_profile_id=profile.id,
            category_id=category.id,
            title="Founder Playbook",
            description="Playbook guide for startups",
            price="29.00",
            status="published",
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

    # 4. Client User
    client_user = db_session.execute(
        select(User).where(User.email == "billing_client@test.com")
    ).scalar_one_or_none()
    if not client_user:
        client_user = User(
            full_name="Alex Client",
            email="billing_client@test.com",
            password_hash="pw_hash",
            phone="+9876543210",
            role="CLIENT",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(client_user)
        db_session.commit()
        db_session.refresh(client_user)

    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "coach": coach,
        "profile": profile,
        "service": service,
        "product": product,
        "client": client_user,
        "headers": headers,
    }


def test_billing_history_unauthorized(client):
    res = client.get("/user/billing-history")
    assert res.status_code == 400
    assert res.json()["error"] == "INVALID_TOKEN"


def test_billing_history_empty_when_no_paid_orders(client, setup_billing_data, db_session):
    setup = setup_billing_data
    buyer = setup["client"]

    # Clear buyer's orders
    db_session.query(Order).filter(Order.user_id == buyer.id).delete()
    db_session.commit()

    res = client.get("/user/billing-history", headers=setup["headers"])
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["status"] == 200
    assert body["message"] == "Billing history retrieved successfully."
    assert body["data"]["total_spent"] == "0.00"
    assert body["data"]["sessions_this_month"] == 0
    assert body["data"]["items"] == []


def test_billing_history_with_paid_and_refunded_orders(client, setup_billing_data, db_session):
    setup = setup_billing_data
    coach = setup["coach"]
    profile = setup["profile"]
    service = setup["service"]
    product = setup["product"]
    buyer = setup["client"]

    # Clean previous
    db_session.query(ProductPurchase).filter(ProductPurchase.user_id == buyer.id).delete()
    db_session.query(ServiceBooking).filter(
        ServiceBooking.order_id.in_(
            db_session.query(Order.id).filter(Order.user_id == buyer.id)
        )
    ).delete(synchronize_session=False)
    db_session.query(Order).filter(Order.user_id == buyer.id).delete()
    db_session.commit()

    now = datetime.now(timezone.utc)
    current_month_date = f"{now.year:04d}-{now.month:02d}-15"

    # 1. Paid Service order in current month (amount: 150.00)
    order_service_paid = Order(
        user_id=buyer.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="service",
        service_id=service.id,
        booking_date=current_month_date,
        booking_time="10:00 AM",
        amount="150.00",
        client_fee="4.50",
        total_amount="154.50",
        coach_fee="7.50",
        coach_earning="142.50",
        currency="USD",
        status="confirmed",
        payment_status="paid",
        transaction_id="pi_test_svc_1",
    )
    db_session.add(order_service_paid)

    # 2. Paid Product order (amount: 29.00)
    order_product_paid = Order(
        user_id=buyer.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="product",
        product_id=product.id,
        amount="29.00",
        client_fee="0.87",
        total_amount="29.87",
        coach_fee="1.45",
        coach_earning="27.55",
        currency="USD",
        status="confirmed",
        payment_status="paid",
        transaction_id="pi_test_prod_1",
    )
    db_session.add(order_product_paid)

    # 3. Refunded Service order (amount: 150.00)
    order_refunded = Order(
        user_id=buyer.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="service",
        service_id=service.id,
        booking_date=current_month_date,
        booking_time="02:00 PM",
        amount="150.00",
        client_fee="4.50",
        total_amount="154.50",
        coach_fee="7.50",
        coach_earning="142.50",
        currency="USD",
        status="cancelled",
        payment_status="refunded",
        transaction_id="pi_test_refund_1",
    )
    db_session.add(order_refunded)

    # 4. Unpaid / expired order (should NOT appear in billing history)
    order_unpaid = Order(
        user_id=buyer.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="service",
        service_id=service.id,
        amount="100.00",
        status="expired",
        payment_status="expired",
    )
    db_session.add(order_unpaid)
    db_session.commit()

    res = client.get("/user/billing-history", headers=setup["headers"])
    assert res.status_code == 200
    data = res.json()["data"]

    # total_spent should only sum active paid items (150.00 + 29.00 = 179.00)
    assert data["total_spent"] == "179.00"
    # sessions_this_month should be 1 (the single confirmed paid service session in current month)
    assert data["sessions_this_month"] == 1

    items = data["items"]
    assert len(items) == 3

    # Check paid service item
    svc_item = next(i for i in items if i["id"] == order_service_paid.id)
    assert svc_item["type"] == "service"
    assert svc_item["title"] == "Strategy Session"
    assert svc_item["coach_name"] == "Sarah Chen"
    assert svc_item["amount"] == "150.00"
    assert svc_item["currency"] == "USD"
    assert svc_item["status"] == "paid"
    assert svc_item["booking_status"] == "confirmed"
    assert svc_item["booking_date"] == current_month_date
    assert svc_item["paid_at"] is not None
    assert svc_item["refunded_at"] is None
    assert f"/api/v1/user/billing-history/{order_service_paid.id}/receipt/" in svc_item["receipt_url"]

    # Check paid product item
    prod_item = next(i for i in items if i["id"] == order_product_paid.id)
    assert prod_item["type"] == "product"
    assert prod_item["title"] == "Founder Playbook"
    assert prod_item["coach_name"] == "Sarah Chen"
    assert prod_item["amount"] == "29.00"
    assert prod_item["status"] == "paid"
    assert prod_item["booking_date"] is None
    assert prod_item["paid_at"] is not None
    assert prod_item["refunded_at"] is None

    # Check refunded service item
    ref_item = next(i for i in items if i["id"] == order_refunded.id)
    assert ref_item["type"] == "service"
    assert ref_item["status"] == "refunded"
    assert ref_item["booking_status"] == "cancelled"
    assert ref_item["refunded_at"] is not None


def test_billing_receipt_endpoint(client, setup_billing_data, db_session):
    setup = setup_billing_data
    coach = setup["coach"]
    profile = setup["profile"]
    service = setup["service"]
    buyer = setup["client"]

    order = Order(
        user_id=buyer.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="service",
        service_id=service.id,
        amount="150.00",
        client_fee="4.50",
        total_amount="154.50",
        coach_fee="7.50",
        coach_earning="142.50",
        currency="USD",
        status="confirmed",
        payment_status="paid",
        transaction_id="pi_receipt_test_123",
    )
    db_session.add(order)
    db_session.commit()

    # 1. Binary PDF receipt (default behavior)
    res_pdf = client.get(
        f"/user/billing-history/{order.id}/receipt",
        headers=setup["headers"],
    )
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers.get("content-type", "")
    assert 'filename="receipt.pdf"' in res_pdf.headers.get("content-disposition", "")
    assert res_pdf.content.startswith(b"%PDF")

    from io import BytesIO
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(res_pdf.content))
    assert len(reader.pages) == 1
    extracted_text = reader.pages[0].extract_text()
    assert "COACH HUB" in extracted_text
    assert f"REC-{order.id:06d}" in extracted_text
    assert "150.00" in extracted_text

    # 2. JSON receipt
    res_json = client.get(
        f"/user/billing-history/{order.id}/receipt/?format=json",
        headers=setup["headers"],
    )
    assert res_json.status_code == 200
    receipt = res_json.json()["data"]
    assert receipt["order_id"] == order.id
    assert receipt["receipt_number"] == f"REC-{order.id:06d}"
    assert receipt["title"] == "Strategy Session"
    assert receipt["coach_name"] == "Sarah Chen"
    assert receipt["client_name"] == "Alex Client"
    assert receipt["amount"] == "150.00"
    assert receipt["client_fee"] == "4.50"
    assert receipt["total_amount"] == "154.50"
    assert receipt["status"] == "paid"
    assert receipt["transaction_id"] == "pi_receipt_test_123"

    # 3. HTML receipt
    res_html = client.get(
        f"/user/billing-history/{order.id}/receipt/",
        headers={**setup["headers"], "Accept": "text/html"},
    )
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers.get("content-type", "")
    assert f"REC-{order.id:06d}" in res_html.text

    # 4. Non-existent receipt -> 404
    res_404 = client.get(
        "/user/billing-history/999999/receipt/",
        headers=setup["headers"],
    )
    assert res_404.status_code == 404
    assert res_404.json()["error"] == "RECEIPT_NOT_FOUND"
