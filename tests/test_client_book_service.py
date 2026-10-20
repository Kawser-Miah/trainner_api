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
def setup_data(db_session):
    # 1. Category
    category = db_session.execute(
        select(Category).where(Category.name == "Business")
    ).scalar_one_or_none()
    if not category:
        category = Category(
            name="Business",
            description="Business coaching",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

    # 2. Coach
    coach_user = db_session.execute(
        select(User).where(User.email == "test_booking_coach@coach.test")
    ).scalar_one_or_none()
    if not coach_user:
        coach_user = User(
            full_name="Sarah Chen",
            email="test_booking_coach@coach.test",
            password_hash="test_hashed_password",
            phone="",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(coach_user)
        db_session.commit()
        db_session.refresh(coach_user)

    coach_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == coach_user.id)
    ).scalar_one_or_none()
    if not coach_profile:
        coach_profile = CoachProfile(
            user_id=coach_user.id,
            headline="Strategy Coach",
            about="I help founders scale.",
            status="approved",
            is_completed=True,
        )
        db_session.add(coach_profile)
        db_session.commit()
        db_session.refresh(coach_profile)

    # 3. Client User
    client_user = db_session.execute(
        select(User).where(User.email == "test_booking_client@coach.test")
    ).scalar_one_or_none()
    if not client_user:
        client_user = User(
            full_name="Thomas Client Jr.",
            email="test_booking_client@coach.test",
            password_hash="test_hashed_password",
            phone="+8801700000001",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(client_user)
        db_session.commit()
        db_session.refresh(client_user)

    # 4. Service
    service = db_session.execute(
        select(CoachService).where(
            CoachService.coach_profile_id == coach_profile.id,
            CoachService.title == "Strategy Session",
        )
    ).scalar_one_or_none()
    if not service:
        service = CoachService(
            coach_profile_id=coach_profile.id,
            category_id=category.id,
            title="Strategy Session",
            description="A 1:1 strategy session.",
            service_type="one_time",
            session_format="video",
            session_duration=60,
            price="160.00",
            currency="USD",
            booking_type="instant",
            status="published",
        )
        db_session.add(service)
        db_session.commit()
        db_session.refresh(service)

    return {
        "category": category,
        "coach_user": coach_user,
        "coach_profile": coach_profile,
        "client_user": client_user,
        "service": service,
    }


def test_book_service_success(client, setup_data):
    client_user = setup_data["client_user"]
    service = setup_data["service"]
    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )

    payload = {
        "service_id": service.id,
        "booking_date": "2026-10-13",
        "booking_time": "02:00 PM",
        "referral_code": "",
    }

    response = client.post(
        "/payments/book-service",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["status"] == 201
    assert data["message"] == "Service order created successfully."

    order = data["data"]
    assert order["id"] is not None
    assert order["user"]["id"] == client_user.id
    assert order["user"]["full_name"] == "Thomas Client Jr."
    assert order["user"]["email"] == "test_booking_client@coach.test"
    assert order["user"]["phone_number"] == "+8801700000001"

    assert order["coach"]["id"] == setup_data["coach_user"].id
    assert order["coach"]["full_name"] == "Sarah Chen"
    assert order["coach"]["about"] == "I help founders scale."

    assert order["service"]["id"] == service.id
    assert order["service"]["title"] == "Strategy Session"
    assert order["service"]["price"] == "160.00"
    assert order["service"]["category"]["name"] == "Business"

    assert order["product"] is None
    assert order["order_type"] == "service"
    assert order["booking_date"] == "2026-10-13"
    assert order["booking_time"] == "02:00 PM"
    assert order["amount"] == "160.00"
    assert order["client_fee"] == "4.80"
    assert order["client_fee_percent"] == "3.00"
    assert order["total_amount"] == "164.80"
    assert order["coach_fee"] == "8.00"
    assert order["coach_fee_percent"] == "5.00"
    assert order["coach_earning"] == "152.00"
    assert order["currency"] == "USD"
    assert order["status"] == "pending"
    assert order["payment_status"] == "pending"
    assert order["is_on_call"] is False
    assert order["created_at"] is not None
    assert order["updated_at"] is not None


def test_book_service_self_booking_prevented(client, setup_data):
    coach_user = setup_data["coach_user"]
    service = setup_data["service"]
    token, _ = create_access_token(
        user_id=coach_user.id,
        role=coach_user.role,
        full_name=coach_user.full_name,
    )

    payload = {
        "service_id": service.id,
        "booking_date": "2026-10-13",
        "booking_time": "02:00 PM",
        "referral_code": "",
    }

    response = client.post(
        "/payments/book-service",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Coach has role COACH, which will either fail client role check or self booking check
    assert response.status_code in [400, 403]


def test_book_service_not_found(client, setup_data):
    client_user = setup_data["client_user"]
    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )

    payload = {
        "service_id": 999999,
        "booking_date": "2026-10-13",
        "booking_time": "02:00 PM",
        "referral_code": "",
    }

    response = client.post(
        "/payments/book-service",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
