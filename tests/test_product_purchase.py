import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.product import CoachProduct
from src.models.client.order import Order
from src.models.client.product_purchase import ProductPurchase
from src.models.client.service_booking import ServiceBooking
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
def setup_product_data(db_session):
    coach = db_session.execute(
        select(User).where(User.email == "coach_product_test@coach.test")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Product Coach",
            email="coach_product_test@coach.test",
            password_hash="pw_hash",
            phone="+1234567899",
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
            headline="Product Specialist",
            about="I write guides.",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    category = db_session.execute(
        select(Category).where(Category.name == "ProductCat")
    ).scalar_one_or_none()
    if not category:
        category = Category(name="ProductCat", description="Digital Guides", is_active=True)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

    product = db_session.execute(
        select(CoachProduct).where(CoachProduct.title == "Test Separation Guide")
    ).scalar_one_or_none()
    if not product:
        product = CoachProduct(
            coach_profile_id=profile.id,
            category_id=category.id,
            title="Test Separation Guide",
            description="A guide for testing DB separation.",
            price="30.00",
            status="published",
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

    buyer = db_session.execute(
        select(User).where(User.email == "buyer_separation@client.test")
    ).scalar_one_or_none()
    if not buyer:
        buyer = User(
            full_name="Separation Buyer",
            email="buyer_separation@client.test",
            password_hash="pw_hash",
            phone="+9876543210",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(buyer)
        db_session.commit()
        db_session.refresh(buyer)

    token, _ = create_access_token(
        user_id=buyer.id,
        role=buyer.role,
        full_name=buyer.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "coach": coach,
        "profile": profile,
        "product": product,
        "buyer": buyer,
        "headers": headers,
    }


def test_purchase_product_creates_separated_order_and_purchase(client, db_session, setup_product_data):
    setup = setup_product_data
    product = setup["product"]
    buyer = setup["buyer"]

    # Clean previous purchases if any
    db_session.query(ProductPurchase).filter(
        ProductPurchase.user_id == buyer.id,
        ProductPurchase.product_id == product.id,
    ).delete()
    db_session.query(Order).filter(
        Order.user_id == buyer.id,
        Order.order_type == "product",
    ).delete()
    db_session.commit()

    res = client.post(
        "/payments/products/purchase",
        json={"product_id": product.id, "referral_code": ""},
        headers=setup["headers"],
    )
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["message"] == "Product purchase order created successfully. Proceed to payment."
    data = body["data"]

    order_id = data["id"]
    assert data["order_type"] == "product"
    assert data["amount"] == "30.00"
    assert data["client_fee"] == "0.90"
    assert data["client_fee_percent"] == "3.00"
    assert data["total_amount"] == "30.90"
    assert data["booking_date"] is None
    assert data["booking_time"] is None
    assert data["service"] is None
    assert data["product"]["id"] == product.id

    # 1. Verify row exists in `orders`
    db_order = db_session.query(Order).filter(Order.id == order_id).first()
    assert db_order is not None
    assert db_order.order_type == "product"
    assert db_order.amount == "30.00"
    assert db_order.client_fee == "0.90"
    assert db_order.client_fee_percent == "3.00"
    assert db_order.total_amount == "30.90"

    # 2. Verify row exists in `product_purchases` with order_id
    db_purchase = db_session.query(ProductPurchase).filter(ProductPurchase.order_id == order_id).first()
    assert db_purchase is not None
    assert db_purchase.user_id == buyer.id
    assert db_purchase.product_id == product.id

    # 3. Verify NO row exists in `service_bookings` for this order
    db_booking = db_session.query(ServiceBooking).filter(ServiceBooking.order_id == order_id).first()
    assert db_booking is None


def test_product_purchase_checkout_and_webhook(client, db_session, setup_product_data, monkeypatch):
    monkeypatch.setattr("src.service.client.booking_and_payments.stripe_webhook_service.settings.stripe_webhook_secret", "")
    setup = setup_product_data
    product = setup["product"]
    buyer = setup["buyer"]

    # Clean
    db_session.query(ProductPurchase).filter(
        ProductPurchase.user_id == buyer.id,
        ProductPurchase.product_id == product.id,
    ).delete()
    db_session.query(Order).filter(
        Order.user_id == buyer.id,
        Order.order_type == "product",
    ).delete()
    db_session.commit()

    # 1. Purchase order
    res = client.post(
        "/payments/products/purchase",
        json={"product_id": product.id},
        headers=setup["headers"],
    )
    assert res.status_code == 201
    order_id = res.json()["data"]["id"]

    # 2. Create Stripe Checkout Session
    res_checkout = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order_id,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
        headers=setup["headers"],
    )
    assert res_checkout.status_code == 200
    checkout_data = res_checkout.json()["data"]
    session_id = checkout_data["session_id"]

    # 3. Webhook call
    webhook_payload = {
        "id": "evt_test_product_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "payment_intent": "pi_prod_test_456",
                "payment_status": "paid",
                "metadata": {
                    "booking_id": str(order_id),
                },
            }
        },
    }

    res_wh = client.post(
        "/payments/stripe/webhook",
        json=webhook_payload,
    )
    assert res_wh.status_code == 200
    wh_data = res_wh.json()
    assert wh_data["received"] is True
    assert wh_data["booking_id"] == order_id
    assert wh_data["status"] == "confirmed"
    assert wh_data["payment_status"] == "paid"

    # Refresh DB and verify
    db_session.expire_all()
    order = db_session.query(Order).filter(Order.id == order_id).first()
    assert order.status == "confirmed"
    assert order.payment_status == "paid"
    assert order.transaction_id == "pi_prod_test_456"

    # Verify product_purchases table has confirmed record
    purchase = db_session.query(ProductPurchase).filter(ProductPurchase.order_id == order_id).first()
    assert purchase is not None
    assert purchase.user_id == buyer.id
    assert purchase.product_id == product.id

