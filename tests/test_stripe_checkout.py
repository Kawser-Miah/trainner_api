from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.service.coach_service import CoachService
from src.models.client.service_order import ServiceOrder
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
def test_setup(db_session):
    # 1. Coach User & Profile
    coach_user = db_session.execute(
        select(User).where(User.email == "test_stripe_coach@coach.test")
    ).scalar_one_or_none()
    if not coach_user:
        coach_user = User(
            full_name="Sarah Coach",
            email="test_stripe_coach@coach.test",
            password_hash="pw_hash",
            phone="+1234567890",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(coach_user)
        db_session.commit()
        db_session.refresh(coach_user)

    profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == coach_user.id)
    ).scalar_one_or_none()
    if not profile:
        profile = CoachProfile(
            user_id=coach_user.id,
            headline="Stripe Test Coach",
            about="Coach for Stripe tests.",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    cat = db_session.execute(
        select(Category).where(Category.name == "Business")
    ).scalar_one_or_none()
    if not cat:
        cat = Category(name="Business", description="Business coaching", is_active=True)
        db_session.add(cat)
        db_session.commit()
        db_session.refresh(cat)

    # 2. Service
    service = db_session.execute(
        select(CoachService).where(CoachService.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not service:
        service = CoachService(
            coach_profile_id=profile.id,
            category_id=cat.id,
            title="Strategy Session",
            description="1:1 Strategy session",
            price="160.00",
            currency="USD",
            session_duration=60,
            status="published",
        )
        db_session.add(service)
        db_session.commit()
        db_session.refresh(service)

    # 3. Client User 1
    client_user = db_session.execute(
        select(User).where(User.email == "test_stripe_client@client.test")
    ).scalar_one_or_none()
    if not client_user:
        client_user = User(
            full_name="Thomas Client",
            email="test_stripe_client@client.test",
            password_hash="pw_hash",
            phone="+1987654321",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(client_user)
        db_session.commit()
        db_session.refresh(client_user)

    # 4. Client User 2 (other client)
    other_client = db_session.execute(
        select(User).where(User.email == "test_stripe_other@client.test")
    ).scalar_one_or_none()
    if not other_client:
        other_client = User(
            full_name="Other Client",
            email="test_stripe_other@client.test",
            password_hash="pw_hash",
            phone="+1112223334",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(other_client)
        db_session.commit()
        db_session.refresh(other_client)

    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    other_token, _ = create_access_token(
        user_id=other_client.id,
        role=other_client.role,
        full_name=other_client.full_name,
    )
    other_headers = {"Authorization": f"Bearer {other_token}"}

    return {
        "coach_user": coach_user,
        "profile": profile,
        "service": service,
        "client_user": client_user,
        "other_client": other_client,
        "headers": headers,
        "other_headers": other_headers,
    }


def test_create_checkout_session_success(client, db_session, test_setup):
    setup = test_setup
    # Create an order
    order = ServiceOrder(
        user_id=setup["client_user"].id,
        coach_id=setup["coach_user"].id,
        coach_profile_id=setup["profile"].id,
        service_id=setup["service"].id,
        order_type="service",
        booking_date="2026-10-28",
        booking_time="02:00 PM",
        amount="160.00",
        client_fee="4.80",
        client_fee_percent="3.00",
        total_amount="164.80",
        coach_fee="8.00",
        coach_fee_percent="5.00",
        coach_earning="152.00",
        currency="USD",
        status="pending",
        payment_status="pending",
        payment_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Call endpoint without /api prefix
    res = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/payment/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": "https://yourapp.com/payment/cancel",
        },
        headers=setup["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == 200
    assert data["message"] == "Checkout session created successfully."

    session_data = data["data"]
    assert session_data["booking_id"] == order.id
    assert "session_id" in session_data
    assert "checkout_url" in session_data
    assert session_data["is_free"] is False
    assert session_data["price"] == "160.00"
    assert session_data["client_fee"] == "4.80"
    assert session_data["client_fee_percent"] == "3.00"
    assert session_data["total"] == "164.80"
    assert session_data["credit_used"] == "0.00"
    assert session_data["payable"] == "164.80"
    assert session_data["currency"] == "USD"

    # Verify DB order updated with transaction_id and payment_method
    db_session.refresh(order)
    assert order.payment_method == "stripe"
    assert order.transaction_id == session_data["session_id"]

    # Also test with /api prefix
    res_api = client.post(
        "/api/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/payment/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": "https://yourapp.com/payment/cancel",
        },
        headers=setup["headers"],
    )
    assert res_api.status_code == 200


def test_create_checkout_session_with_credit(client, db_session, test_setup):
    setup = test_setup
    order = ServiceOrder(
        user_id=setup["client_user"].id,
        coach_id=setup["coach_user"].id,
        coach_profile_id=setup["profile"].id,
        service_id=setup["service"].id,
        order_type="service",
        booking_date="2026-10-28",
        booking_time="03:00 PM",
        amount="160.00",
        client_fee="4.80",
        client_fee_percent="3.00",
        total_amount="164.80",
        currency="USD",
        status="pending",
        payment_status="pending",
        payment_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Pass credit_used: 10.00
    res = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "credit_used": "10.00",
            "success_url": "https://yourapp.com/payment/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": "https://yourapp.com/payment/cancel",
        },
        headers=setup["headers"],
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["price"] == "160.00"
    assert data["client_fee"] == "4.80"
    assert data["client_fee_percent"] == "3.00"
    assert data["total"] == "164.80"
    assert data["credit_used"] == "10.00"
    assert data["payable"] == "154.80"
    assert data["is_free"] is False


def test_create_checkout_session_unauthorized(client, db_session, test_setup):
    setup = test_setup
    order = ServiceOrder(
        user_id=setup["client_user"].id,
        coach_id=setup["coach_user"].id,
        coach_profile_id=setup["profile"].id,
        service_id=setup["service"].id,
        order_type="service",
        booking_date="2026-10-28",
        booking_time="04:00 PM",
        amount="160.00",
        total_amount="164.80",
        status="pending",
        payment_status="pending",
        payment_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # 1. No auth header -> 400 / 401
    res1 = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
    )
    assert res1.status_code in [400, 401, 403]

    # 2. Other client tries to pay for this booking -> 403
    res2 = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
        headers=setup["other_headers"],
    )
    assert res2.status_code == 403
    assert res2.json()["error"] == "FORBIDDEN"


def test_create_checkout_session_not_found(client, test_setup):
    res = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": 999999,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
        headers=test_setup["headers"],
    )
    assert res.status_code == 404
    assert res.json()["error"] == "BOOKING_NOT_FOUND"


def test_create_checkout_session_expired(client, db_session, test_setup):
    setup = test_setup
    order = ServiceOrder(
        user_id=setup["client_user"].id,
        coach_id=setup["coach_user"].id,
        coach_profile_id=setup["profile"].id,
        service_id=setup["service"].id,
        order_type="service",
        booking_date="2026-10-28",
        booking_time="05:00 PM",
        amount="160.00",
        total_amount="164.80",
        status="pending",
        payment_status="pending",
        payment_due_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired!
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    res = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
        headers=setup["headers"],
    )
    assert res.status_code == 400
    assert res.json()["error"] == "BOOKING_EXPIRED"


def test_create_checkout_session_already_paid(client, db_session, test_setup):
    setup = test_setup
    order = ServiceOrder(
        user_id=setup["client_user"].id,
        coach_id=setup["coach_user"].id,
        coach_profile_id=setup["profile"].id,
        service_id=setup["service"].id,
        order_type="service",
        booking_date="2026-10-28",
        booking_time="06:00 PM",
        amount="160.00",
        total_amount="164.80",
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    res = client.post(
        "/payments/stripe/create-checkout-session",
        json={
            "booking_id": order.id,
            "success_url": "https://yourapp.com/success",
            "cancel_url": "https://yourapp.com/cancel",
        },
        headers=setup["headers"],
    )
    assert res.status_code == 400
    assert res.json()["error"] == "ALREADY_PAID"
